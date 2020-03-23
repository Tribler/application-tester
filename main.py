from __future__ import absolute_import

import argparse
import logging
from asyncio import get_event_loop, ensure_future
from pathlib import Path

from tribler_apptester.executor import Executor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a Tribler application test.')
    parser.add_argument('tribler_executable', metavar='path', type=str, help='the full path to the Tribler executable')
    parser.add_argument('-p', '--plain', action='store_true', help='allow plain downloads')
    parser.add_argument('-d', '--duration', default=None, type=int, help='run the Tribler application tester for a specific period of time')
    parser.add_argument('-s', '--silent', action='store_true', help='do not execute random actions')
    parser.add_argument('--codeport', default=5500, type=int, help='the port used to execute code')
    parser.add_argument('--monitordownloads', default=None, type=int, help='monitor the downloads with a specified interval in seconds')
    parser.add_argument('--monitorresources', default=None, type=int, help='monitor the resources with a specified interval in seconds')
    parser.add_argument('--monitoripv8', default=None, type=int, help='monitor IPv8 overlays with a specified interval in seconds')
    parser.add_argument('--magnetsfile', default=Path("tribler_apptester") / "data" / "torrent_links.txt", type=str, help='specify the location of the file with magnet links')

    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    args = parser.parse_args()
    executor = Executor(args)

    loop = get_event_loop()
    coro = executor.start()
    ensure_future(coro)
    loop.run_forever()
