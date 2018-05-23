import argparse

from twisted.internet import reactor

from executor import Executor


def start_executor(args):
    executor = Executor(args.tribler_executable)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tribler application test.')
    parser.add_argument('tribler_executable', metavar='path', type=str, help='the full path to the Tribler executable')

    args = parser.parse_args()

    reactor.callWhenRunning(start_executor, args)
    reactor.run()
