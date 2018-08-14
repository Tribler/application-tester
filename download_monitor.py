import json
import os

import time
from twisted.internet.task import LoopingCall

from requestmgr import HTTPRequestManager


class DownloadMonitor(object):
    """
    This class is responsible for monitoring downloads in Tribler.
    Specifically, it fetches information from the Tribler core and writes it to a file.
    """

    def __init__(self, interval):
        self.interval = interval
        self.request_manager = HTTPRequestManager()
        self.monitor_lc = LoopingCall(self.monitor_downloads)
        self.start_time = time.time()

        # Create the output directory if it does not exist yet
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.download_stats_file_path = os.path.join(output_dir, 'download_stats.csv')
        with open(self.download_stats_file_path, "w") as output_file:
            output_file.write("time,infohash,status,speed_up,speed_down\n")

    def start(self):
        """
        Start the monitoring loop for the downloads.
        """
        self.monitor_lc.start(self.interval)

    def on_downloads(self, response):
        downloads = json.loads(response)
        for download in downloads["downloads"]:
            with open(self.download_stats_file_path, "a") as output_file:
                time_diff = time.time() - self.start_time
                output_file.write("%s,%s,%s,%s,%s\n" % (time_diff,
                                                        download["infohash"],
                                                        download["status"],
                                                        download["speed_up"],
                                                        download["speed_down"]))

    def monitor_downloads(self):
        """
        Monitor the downloads in Tribler.
        """
        return self.request_manager.get_downloads().addCallback(self.on_downloads)
