import argparse

import logging
from twisted.internet import reactor

from executor import Executor


def start_executor(args):
    executor = Executor(args.tribler_executable, args.plain)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tribler application test.')
    parser.add_argument('tribler_executable', metavar='path', type=str, help='the full path to the Tribler executable')
    parser.add_argument('-p', '--plain', default=False, type=bool, help='allow plain downloads')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    reactor.callWhenRunning(start_executor, args)
    reactor.run()
