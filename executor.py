import logging
import os
import subprocess
from base64 import b64encode
from bisect import bisect
from random import random, randint, choice
import sys
import time

import signal
from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.error import ConnectionRefusedError
from twisted.internet.task import LoopingCall

from actions.browse_discovered_action import BrowseDiscoveredAction
from actions.change_anonymity_action import ChangeAnonymityAction
from actions.change_download_files_action import ChangeDownloadFilesAction
from actions.explore_channel_action import ExploreChannelAction
from actions.explore_download_action import ExploreDownloadAction
from actions.page_action import RandomPageAction
from actions.screenshot_action import ScreenshotAction
from actions.search_action import RandomSearchAction
from actions.shutdown_action import ShutdownAction
from actions.start_download_action import StartRandomDownloadAction
from actions.remove_download_action import RemoveRandomDownloadAction
from actions.start_vod_action import StartVODAction
from actions.subscribe_unsubscribe_action import SubscribeUnsubscribeAction
from actions.wait_action import WaitAction
from monitors.download_monitor import DownloadMonitor
from monitors.ipv8_monitor import IPv8Monitor
from ircclient import IRCManager
from requestmgr import HTTPRequestManager
from monitors.resource_monitor import ResourceMonitor
from tcpsocket import TriblerCodeClientFactory


class Executor(object):

    def __init__(self, args):
        self.args = args
        self.tribler_path = args.tribler_executable
        self.code_port = args.code_port
        self._logger = logging.getLogger(self.__class__.__name__)
        self.allow_plain_downloads = args.plain
        self.magnets_file_path = args.magnetsfile
        self.pending_tasks = {}  # Dictionary of pending tasks
        self.probabilities = []
        self.socket_factory = TriblerCodeClientFactory(self)
        self.code_socket = None
        self.start_time = time.time()
        self.request_manager = HTTPRequestManager()
        self.irc_manager = None
        self.tribler_crashed = False
        self.download_monitor = None
        self.resource_monitor = None
        self.ipv8_monitor = None
        self.random_action_lc = None
        self.tribler_started_lc = None
        self.tribler_started_checks = 1
        self.tribler_stopped_lc = None
        self.tribler_stopped_checks = 1
        self.tribler_process = None
        self.shutting_down = False

        self.start_tribler()

        if args.duration:
            reactor.callLater(args.duration, self.stop, 0)

    def check_tribler(self):
        """
        Check the state of Tribler.
        """
        def on_state(_):
            # It seems Tribler is already running; open the socket
            self._logger.info("Tribler already running - opening socket")
            self.open_code_socket()

        def on_error(failure):
            # We got an error, check whether it is ConnectionRefused. If so, start Tribler
            if isinstance(failure.value, ConnectionRefusedError):
                self.start_tribler()

        self.request_manager.get_state().addCallbacks(on_state, on_error)

    def start_tribler(self):
        """
        Start Tribler if it has not been started yet.
        """
        self._logger.info("Tribler not running - starting it")
        self.tribler_process = subprocess.Popen("%s --allow-code-injection --testnet" % self.tribler_path, shell=True)
        reactor.callLater(5, self.check_tribler_started)

    def check_tribler_started(self):
        self._logger.info("Checking whether Tribler has started (%d/10)", self.tribler_started_checks)

        def on_response(started):
            if started:
                self.open_code_socket()
            elif self.tribler_started_checks == 10:
                self._logger.error("Tribler did not seem to start within reasonable time, bailing out")
                self.shutdown_tester(1)
            else:
                self.tribler_started_checks += 1
                reactor.callLater(5, self.check_tribler_started)

        return self.request_manager.is_tribler_started().addCallback(on_response)

    def open_code_socket(self):
        self._logger.info("Opening Tribler code socket connection")
        reactor.connectTCP("localhost", 5500, self.socket_factory)

    def on_socket_ready(self, socket):
        self.code_socket = socket
        self.determine_probabilities()

        if self.args.ircid:
            self.irc_manager = IRCManager(self, self.args.ircid)
            self.irc_manager.start()

        if not self.args.silent:
            self.random_action_lc = LoopingCall(self.perform_random_action)
            self.random_action_lc.start(15)

        if self.args.monitordownloads:
            self.download_monitor = DownloadMonitor(self.args.monitordownloads)
            reactor.callLater(18, self.download_monitor.start)

        if self.args.monitorresources:
            self.resource_monitor = ResourceMonitor(self.args.monitorresources)
            reactor.callLater(20, self.resource_monitor.start)

        if self.args.monitoripv8:
            self.ipv8_monitor = IPv8Monitor(self.args.monitoripv8)
            reactor.callLater(20, self.ipv8_monitor.start)

    def on_socket_failed(self, failure):
        self._logger.error("Tribler code socket connection failed: %s", failure)
        self.stop(1)

    def determine_probabilities(self):
        with open(os.path.join(os.getcwd(), "data", "action_weights.txt"), "r") as action_weights_file:
            content = action_weights_file.read()
            for line in content.split('\n'):
                if len(line) == 0:
                    continue

                if line.startswith('#'):
                    continue

                parts = line.split('=')
                if len(parts) < 2:
                    continue

                self.probabilities.append((parts[0], int(parts[1])))

    def stop(self, exit_code):
        """
        Stop the application. First, shutdown Tribler (gracefully) and then shutdown the application tester.
        """
        if self.shutting_down:
            return

        self.shutting_down = True
        self._logger.info("About to shutdown Tribler")
        if self.download_monitor:
            self.download_monitor.stop()
            self.download_monitor = None
        if self.resource_monitor:
            self.resource_monitor.stop()
            self.resource_monitor = None
        if self.random_action_lc:
            self.random_action_lc.stop()
            self.random_action_lc = None

        if self.code_socket:
            self.execute_action(ShutdownAction())

        if sys.platform == "win32":
            os.system("taskkill /im tribler.exe")
        elif sys.platform == "darwin":
            os.kill(self.tribler_process.pid, signal.SIGINT)
        else:
            os.kill(self.tribler_process.pid, signal.SIGTERM)

        reactor.callLater(5, self.check_tribler_shutdown, exit_code)

    @inlineCallbacks
    def check_tribler_shutdown(self, exit_code):
        tribler_stopped = yield self.request_manager.is_tribler_stopped()
        if tribler_stopped:
            self.on_tribler_shutdown(exit_code)
        elif self.tribler_stopped_checks == 10:
            self._logger.warning("Tribler did not shutdown in reasonable time; force kill it")
            if sys.platform == "win32":
                os.system("taskkill /im tribler.exe /f")
            else:
                os.kill(self.tribler_process.pid, signal.SIGKILL)
            self.on_tribler_shutdown(exit_code)
        else:
            # Still alive, schedule next check
            self.tribler_stopped_checks += 1
            reactor.callLater(5, self.check_tribler_shutdown, exit_code)

    def on_tribler_shutdown(self, exit_code):
        self._logger.info("Stopped Tribler, shutting down")
        self.shutdown_tester(exit_code)

    def shutdown_tester(self, exit_code):
        reactor.addSystemEventTrigger('after', 'shutdown', os._exit, exit_code)
        reactor.stop()

    @property
    def uptime(self):
        return time.time() - self.start_time

    def on_task_result(self, task_id, result):
        """
        A task has completed. Invoke the task completion callback with the result.
        """
        if task_id in self.pending_tasks:
            self.pending_tasks[task_id].callback(result)
            self.pending_tasks.pop(task_id, None)

    def on_tribler_crash(self, traceback):
        """
        Tribler has crashed. Handle the error and shut everything down.
        """
        self._logger.error("********** TRIBLER CRASHED **********")
        self._logger.error("Tribler crashed after uptime of %s sec! Stack trace: %s", self.uptime, traceback)
        self.tribler_crashed = True
        if self.irc_manager:
            self.irc_manager.irc.send_channel_message("Tribler crashed with stack trace: %s" % traceback)
        self.stop(1)

    def weighted_choice(self, choices):
        if len(choices) == 0:
            return None
        values, weights = zip(*choices)
        total = 0
        cum_weights = []
        for w in weights:
            total += w
            cum_weights.append(total)
        x = random() * total
        i = bisect(cum_weights, x)
        return values[i]

    def get_rand_bool(self):
        return randint(0, 1) == 0

    def execute_action(self, action):
        """
        Execute a given action and return a deferred that fires with the result of the action.
        """
        self._logger.info("Executing action: %s" % action)

        task_id = ''.join(choice('0123456789abcdef') for _ in range(10)).encode('utf-8')
        task_deferred = Deferred()
        self.pending_tasks[task_id] = task_deferred

        code = """return_value = ''

def exit_script():
    import sys
    print('Execution of task %s completed')
    sys.exit(0)\n\n""" % task_id.decode('utf-8')

        code += action.generate_code() + '\nexit_script()'
        base64_code = b64encode(code.encode('utf-8'))

        # Let Tribler execute this code
        self.execute_code(base64_code, task_id)

        return task_deferred

    def execute_code(self, base64_code, task_id):
        self._logger.info("Executing code with task id: %s" % task_id.decode('utf-8'))
        self.code_socket.run_code(base64_code, task_id)

    def perform_random_action(self):
        """
        This method performs a random action in Tribler.
        There are various actions possible that can occur with different probabilities.
        """
        action = self.weighted_choice(self.probabilities)
        if not action:
            self._logger.warning("No action available!")
            self.execute_action(WaitAction(1000))
            return
        self._logger.info("Performing action: %s", action)
        if action == 'random_page':
            action = RandomPageAction()
        elif action == 'search':
            action = RandomSearchAction()
        elif action == 'start_download':
            action = StartRandomDownloadAction(self.magnets_file_path)
        elif action == 'remove_download':
            action = RemoveRandomDownloadAction()
        elif action == 'explore_download':
            action = ExploreDownloadAction()
        elif action == 'browse_discovered':
            action = BrowseDiscoveredAction()
        elif action == 'explore_channel':
            action = ExploreChannelAction()
        elif action == 'screenshot':
            action = ScreenshotAction()
        elif action == 'start_vod':
            action = StartVODAction()
        elif action == 'change_anonymity':
            action = ChangeAnonymityAction(allow_plain=self.allow_plain_downloads)
        elif action == 'subscribe_unsubscribe':
            action = SubscribeUnsubscribeAction()
        elif action == 'change_download_files':
            action = ChangeDownloadFilesAction()

        self.execute_action(action)
