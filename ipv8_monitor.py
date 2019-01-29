import json
import os

import time
from twisted.internet.task import LoopingCall

from requestmgr import HTTPRequestManager


class IPv8Monitor(object):
    """
    This class is responsible for monitoring IPv8 within Tribler.
    Specifically, it fetches information from the Tribler core and writes it to a file.
    """

    def __init__(self, interval):
        self.interval = interval
        self.request_manager = HTTPRequestManager()
        self.monitor_lc = LoopingCall(self.monitor_ipv8)
        self.start_time = time.time()

        # Create the output directory if it does not exist yet
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.overlay_stats_file_path = os.path.join(output_dir, 'ipv8_overlay_stats.csv')
        with open(self.overlay_stats_file_path, "w") as output_file:
            output_file.write("time,overlay_id,num_peers\n")

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

    def on_overlay_statistics(self, response):
        statistics = json.loads(response)
        if 'ipv8_overlay_statistics' not in statistics:
            return

        for overlay in statistics["ipv8_overlay_statistics"]:
            with open(self.overlay_stats_file_path, "a") as output_file:
                time_diff = time.time() - self.start_time
                output_file.write("%s,%s,%d\n" % (time_diff, overlay['master_peer'][-6:], len(overlay['peers'])))

    def monitor_ipv8(self):
        """
        Monitor IPv8.
        """
        return self.request_manager.get_overlay_statistics().addCallback(self.on_overlay_statistics)
