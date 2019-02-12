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

        self.circuits_file_path = os.path.join(output_dir, 'circuits.csv')
        with open(self.circuits_file_path, "w") as output_file:
            output_file.write("time,id,type,state,goal_hops,actual_hops,bytes_up,bytes_down\n")

        self.circuits_states_file_path = os.path.join(output_dir, 'circuit_states.csv')
        with open(self.circuits_states_file_path, "w") as output_file:
            output_file.write("time,ready,extending,closing\n")

        self.circuits_types_file_path = os.path.join(output_dir, 'circuit_types.csv')
        with open(self.circuits_types_file_path, "w") as output_file:
            output_file.write("time,data,ip,rp,rendezvous\n")

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
        time_diff = time.time() - self.start_time
        circuits_ready = circuits_extending = circuits_closing = 0
        circuits_data = circuits_ip = circuits_rp = circuits_rendezvous = 0

        for circuit in circuits_info["circuits"]:
            if circuit["state"] == "READY":
                circuits_ready += 1
            elif circuit["state"] == "EXTENDING":
                circuits_extending += 1
            elif circuit["state"] == "CLOSING":
                circuits_closing += 1

            if circuit["type"] == "DATA":
                circuits_data += 1
            elif circuit["type"] == "IP":
                circuits_ip += 1
            elif circuit["type"] == "RP":
                circuits_rp += 1
            elif circuit["type"] == "RENDEZVOUS":
                circuits_rendezvous += 1

            with open(self.circuits_file_path, "a") as output_file:
                output_file.write("%s,%s,%s,%s,%d,%d,%d,%d\n" % (time_diff,
                                                                 circuit["circuit_id"],
                                                                 circuit["type"],
                                                                 circuit["state"],
                                                                 circuit["goal_hops"],
                                                                 circuit["actual_hops"],
                                                                 circuit["bytes_up"],
                                                                 circuit["bytes_down"]))

        with open(self.circuits_states_file_path, "a") as output_file:
            output_file.write("%s,%d,%d,%d\n" % (time_diff,
                                                 circuits_ready,
                                                 circuits_extending,
                                                 circuits_closing))

        with open(self.circuits_types_file_path, "a") as output_file:
            output_file.write("%s,%d,%d,%d,%d\n" % (time_diff,
                                                    circuits_data,
                                                    circuits_ip,
                                                    circuits_rp,
                                                    circuits_rendezvous))

    def monitor_downloads(self):
        """
        Monitor the downloads in Tribler.
        """
        return self.request_manager.get_downloads().addCallback(self.on_downloads)
