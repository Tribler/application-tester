import argparse
import sys

import logging
from twisted.internet import reactor
from twisted.python import log

from executor import Executor


def start_executor(args):
    executor = Executor(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tribler application test.')
    parser.add_argument('tribler_executable', metavar='path', type=str, help='the full path to the Tribler executable')
    parser.add_argument('-p', '--plain', default=False, type=bool, help='allow plain downloads')
    parser.add_argument('-i', '--ircid', default=None, type=str, help='join IRC with the specified ID')
    parser.add_argument('-d', '--duration', default=None, type=int, help='run the Tribler application tester for a specific period of time')
    parser.add_argument('--monitordownloads', default=None, type=int, help='monitor the downloads with a specified interval in seconds')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    log.startLogging(sys.stdout)

    reactor.callWhenRunning(start_executor, args)
    reactor.run()
