from __future__ import absolute_import

import json
import logging

from twisted.internet import reactor
from twisted.internet.defer import fail, Deferred
from twisted.internet.error import ConnectionRefusedError
from twisted.web import http
from twisted.web.client import readBody, Agent
from twisted.web.http_headers import Headers


def http_get(uri, headers):
    """
    Performs a GET request
    :param uri: The URL to perform a GET request to
    :param headers: Headers for the request. X-Api-key is included in the headers.
    :return: A deferred firing the body of the response.
    :raises HttpError: When the HTTP response code is not OK (i.e. not the HTTP Code 200)
    """
    def _on_response(response):
        if response.code == http.OK:
            return readBody(response)
        raise RuntimeError(response)

    try:
        agent = Agent(reactor)
        deferred = agent.request(b'GET', uri, headers, None)

        deferred.addCallback(_on_response)
        return deferred
    except:
        return fail()


class HTTPRequestManager(object):
    """
    This class manages requests to the Tribler core.
    """

    def __init__(self, api_key):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.headers = Headers({'User-Agent': ['Tribler application tester'], 'X-Api-Key': [api_key]})

    def get_token_balance(self):
        """
        Perform a request to the core to get the token balance.
        """
        def on_wallets_response(response):
            json_response = json.loads(response)
            if "MB" not in json_response["wallets"]:
                return 0
            return json_response["wallets"]["MB"]["balance"]["available"]

        return http_get(b"http://localhost:8085/wallets", self.headers).addCallback(on_wallets_response)

    def get_downloads(self):
        """
        Perform a request to the core to get the downloads
        """
        return http_get(b"http://localhost:8085/downloads", self.headers)

    def get_circuits_info(self):
        """
        Perform a request to the core to get circuits information
        """
        return http_get(b"http://localhost:8085/ipv8/tunnel/circuits", self.headers)

    def get_overlay_statistics(self):
        """
        Perform a request to the core to get IPv8 overlay statistics
        """
        return http_get(b"http://localhost:8085/ipv8/overlays", self.headers)

    def get_memory_history_core(self):
        """
        Perform a request to the core to get the memory usage history
        """
        return http_get(b"http://localhost:8085/debug/memory/history", self.headers)

    def get_cpu_history_core(self):
        """
        Perform a request to the core to get the CPU usage history
        """
        return http_get(b"http://localhost:8085/debug/cpu/history", self.headers)

    def get_state(self):
        """
        Get the current state of the Tribler instance
        """
        return http_get(b"http://localhost:8085/state", self.headers)

    def is_tribler_started(self):
        """
        Return whether Tribler has started or not
        """
        started_deferred = Deferred()

        def on_response(response):
            json_response = json.loads(response)
            started_deferred.callback(json_response['state'] == 'STARTED')

        def on_error(failure):
            self._logger.error(failure)
            started_deferred.callback(False)

        self.get_state().addCallbacks(on_response, on_error)
        return started_deferred

    def is_tribler_stopped(self):
        """
        Return whether Tribler has started or not
        """
        stopped_deferred = Deferred()

        def on_response(_):
            stopped_deferred.callback(False)

        def on_error(_):
            stopped_deferred.callback(True)

        self.get_state().addCallbacks(on_response, on_error)
        return stopped_deferred
