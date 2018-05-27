import logging
import os
from bisect import bisect
from random import random, randint, choice

from twisted.internet.task import LoopingCall

from actions.browse_discovered_action import BrowseDiscoveredAction
from actions.explore_channel_action import ExploreChannelAction
from actions.explore_download_action import ExploreDownloadAction
from actions.page_action import RandomPageAction
from actions.screenshot_action import ScreenshotAction
from actions.search_action import RandomSearchAction
from actions.start_download_action import StartRandomDownloadAction
from actions.remove_download_action import RemoveRandomDownloadAction


class Executor(object):

    def __init__(self, tribler_path):
        self.tribler_path = tribler_path
        self._logger = logging.getLogger(self.__class__.__name__)

        self.random_action_lc = LoopingCall(self.perform_random_action)
        self.random_action_lc.start(15)

        self.check_task_completion_lc = LoopingCall(self.check_task_completion)
        self.check_task_completion_lc.start(2)

    def check_task_completion(self):
        """
        This method periodically checks whether Python scripts have been completed.
        Completion of such a script is indicated by presence of a .done file.
        """
        for file in os.listdir(os.path.join(os.getcwd(), "tmp_scripts")):
            if file.endswith(".done"):
                task_id = file[:-5]
                self._logger.info("Task with ID %s completed!", task_id)
                os.remove(os.path.join(os.getcwd(), "tmp_scripts", file))

                python_file_path = os.path.join(os.getcwd(), "tmp_scripts", "%s.py" % task_id)
                if os.path.exists(python_file_path):
                    os.remove(python_file_path)

    def weighted_choice(self, choices):
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
        Execute a given action.
        """
        self._logger.info("Executing action: %s" % action)

        task_id = ''.join(choice('0123456789abcdef') for _ in xrange(10))
        tmp_scripts_dir = os.path.join(os.getcwd(), "tmp_scripts")
        code_file_path = os.path.join(tmp_scripts_dir, "%s.py" % task_id)

        # First, write a function to end the program to the file
        code = """def exit_script():
    import sys
    open('%s', 'a').close()
    sys.exit(0)\n\n""" % (os.path.join(tmp_scripts_dir, "%s.done" % task_id))

        code += action.generate_code() + '\nexit_script()'

        # Write the generated code to a separate file
        with open(code_file_path, "wb") as code_file:
            code_file.write(code)

        # Let Tribler execute this code
        self.execute_code(code_file_path)

    def execute_code(self, code_file_path):
        self._logger.info("Executing code file: %s" % code_file_path)
        os.system("%s \"code:%s\"" % (self.tribler_path, code_file_path))

    def perform_random_action(self):
        """
        This method performs a random action in Tribler. There are various actions possible that can occur with
        different probabilities.
        """
        probs = [('random_page', 30), ('search', 15), ('start_download', 20), ('remove_download', 5), ('explore_download', 10), ('browse_discovered', 10), ('explore_channel', 10)]
        action = self.weighted_choice(probs)
        self._logger.info("Performing action: %s", action)
        if action == 'random_page':
            action = RandomPageAction()
        elif action == 'search':
            action = RandomSearchAction()
        elif action == 'start_download':
            action = StartRandomDownloadAction()
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

        self.execute_action(action)
