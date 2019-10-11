from __future__ import absolute_import

import argparse
import os
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
    parser.add_argument('code_port', metavar='port', type=int, help='the port used to execute code')
    parser.add_argument('-p', '--plain', action='store_true', help='allow plain downloads')
    parser.add_argument('-i', '--ircid', default=None, type=str, help='join IRC with the specified ID')
    parser.add_argument('-d', '--duration', default=None, type=int, help='run the Tribler application tester for a specific period of time')
    parser.add_argument('-s', '--silent', action='store_true', help='do not execute random actions')
    parser.add_argument('--monitordownloads', default=None, type=int, help='monitor the downloads with a specified interval in seconds')
    parser.add_argument('--monitorresources', default=None, type=int, help='monitor the resources with a specified interval in seconds')
    parser.add_argument('--monitoripv8', default=None, type=int, help='monitor IPv8 overlays with a specified interval in seconds')
    parser.add_argument('--magnetsfile', default=os.path.join('data', 'torrent_links.txt'), type=str, help='specify the location of the file with magnet links')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    log.startLogging(sys.stdout)

    reactor.callWhenRunning(start_executor, args)
    reactor.run()
