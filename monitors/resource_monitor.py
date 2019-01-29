import json
import os

import time
from twisted.internet.task import LoopingCall

from requestmgr import HTTPRequestManager


class ResourceMonitor(object):
    """
    This class is responsible for monitoring resources in Tribler.
    Specifically, it fetches information from the Tribler core and writes it to a file.
    """

    def __init__(self, interval):
        self.interval = interval
        self.request_manager = HTTPRequestManager()
        self.monitor_memory_lc = LoopingCall(self.monitor_memory)
        self.monitor_cpu_lc = LoopingCall(self.monitor_cpu)
        self.start_time = time.time()
        self.latest_memory_time = 0
        self.latest_cpu_time = 0

        # Create the output directory if it does not exist yet
        output_dir = os.path.join(os.getcwd(), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.memory_stats_file_path = os.path.join(output_dir, 'memory_stats.csv')
        with open(self.memory_stats_file_path, "w") as output_file:
            output_file.write("time,memory_usage\n")

        self.cpu_stats_file_path = os.path.join(output_dir, 'cpu_stats.csv')
        with open(self.cpu_stats_file_path, "w") as output_file:
            output_file.write("time,cpu_usage\n")

    def start(self):
        """
        Start the monitoring loop for the resources.
        """
        self.monitor_memory_lc.start(self.interval)
        self.monitor_cpu_lc.start(self.interval)

    def stop(self):
        """
        Stop the monitoring loop for the resources.
        """
        if self.monitor_memory_lc and self.monitor_memory_lc.running:
            self.monitor_memory_lc.stop()
            self.monitor_memory_lc = None

        if self.monitor_cpu_lc and self.monitor_cpu_lc.running:
            self.monitor_cpu_lc.stop()
            self.monitor_cpu_lc = None

    def on_memory_history(self, response):
        history = json.loads(response)
        for history_item in history["memory_history"]:
            if history_item["time"] > self.latest_memory_time:
                self.latest_memory_time = history_item["time"]
                time_diff = history_item["time"] - self.start_time
                with open(self.memory_stats_file_path, "a") as output_file:
                    output_file.write("%s,%s\n" % (time_diff, history_item["mem"]))

    def on_cpu_history(self, response):
        history = json.loads(response)
        for history_item in history["cpu_history"]:
            if history_item["time"] > self.latest_cpu_time:
                self.latest_cpu_time = history_item["time"]
                time_diff = history_item["time"] - self.start_time
                with open(self.cpu_stats_file_path, "a") as output_file:
                    output_file.write("%s,%s\n" % (time_diff, history_item["cpu"]))

    def monitor_memory(self):
        """
        Monitor the memory usage in Tribler.
        """
        return self.request_manager.get_memory_history_core().addCallback(self.on_memory_history)

    def monitor_cpu(self):
        """
        Monitor the CPU usage in Tribler.
        """
        return self.request_manager.get_cpu_history_core().addCallback(self.on_cpu_history)
