import logging
import os
from bisect import bisect
from random import random, randint

from twisted.internet.task import LoopingCall

from actions.page_action import RandomPageAction
from actions.search_action import RandomSearchAction
from actions.start_download_action import StartRandomDownloadAction
from actions.stop_download_action import StopRandomDownloadAction


class Executor(object):

    def __init__(self, tribler_path):
        self.tribler_path = tribler_path
        self._logger = logging.getLogger(self.__class__.__name__)

        self.random_action_lc = LoopingCall(self.perform_random_action)
        self.random_action_lc.start(10)

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
        self.execute_code(action.generate_code())

    def execute_code(self, code):
        print code
        self._logger.info("Executing code: %s" % code[:100])
        os.system("%s \"%s\"" % (self.tribler_path, code))

    def perform_random_action(self):
        """
        This method performs a random action in Tribler. There are various actions possible that can occur with
        different probabilities.
        """
        probs = [('random_page', 50), ('search', 25), ('start_download', 20), ('stop_download', 5)]
        action = self.weighted_choice(probs)
        self._logger.info("Performing action: %s", action)
        if action == 'random_page':
            action = RandomPageAction()
        elif action == 'search':
            action = RandomSearchAction()
        elif action == 'start_download':
            action = StartRandomDownloadAction()
        elif action == 'stop_download':
            action = StopRandomDownloadAction()

        self.execute_action(action)
