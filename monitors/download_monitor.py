import json
import os

import time
from twisted.internet.task import LoopingCall

from requestmgr import HTTPRequestManager


class DownloadMonitor(object):
    """
    This class is responsible for monitoring downloads and circuits in Tribler.
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
            output_file.write("time,infohash,status,speed_up,speed_down,progress\n")

        self.circuits_stats_file_path = os.path.join(output_dir, 'circuit_stats.csv')
        with open(self.circuits_stats_file_path, "w") as output_file:
            output_file.write("time,num_circuits\n")

    def start(self):
        """
        Start the monitoring loop for the downloads.
        """
        self.monitor_lc.start(self.interval)

    def stop(self):
        """
        Stop the monitoring loop for the downloads.
        """
        if self.monitor_lc and self.monitor_lc.running:
            self.monitor_lc.stop()
            self.monitor_lc = None

    def on_downloads(self, response):
        downloads = json.loads(response)
        for download in downloads["downloads"]:
            with open(self.download_stats_file_path, "a") as output_file:
                time_diff = time.time() - self.start_time
                output_file.write("%s,%s,%s,%s,%s,%f\n" % (time_diff,
                                                           download["infohash"],
                                                           download["status"],
                                                           download["speed_up"],
                                                           download["speed_down"],
                                                           download["progress"]))

        # Now we get the number of circuits
        return self.request_manager.get_circuits_info().addCallback(self.on_circuits_info)

    def on_circuits_info(self, response):
        circuits_info = json.loads(response)
        with open(self.circuits_stats_file_path, "a") as output_file:
            time_diff = time.time() - self.start_time
            output_file.write("%s,%d\n" % (time_diff, len(circuits_info['circuits'])))

    def monitor_downloads(self):
        """
        Monitor the downloads in Tribler.
        """
        return self.request_manager.get_downloads().addCallback(self.on_downloads)
