import json

from twisted.internet import reactor
from twisted.internet.defer import fail
from twisted.web import http
from twisted.web.client import readBody, Agent
from twisted.web.http_headers import Headers


def http_get(uri):
    """
    Performs a GET request
    :param uri: The URL to perform a GET request to
    :return: A deferred firing the body of the response.
    :raises HttpError: When the HTTP response code is not OK (i.e. not the HTTP Code 200)
    """
    def _on_response(response):
        if response.code == http.OK:
            return readBody(response)
        raise RuntimeError(response)

    try:
        agent = Agent(reactor)
        deferred = agent.request('GET', uri, Headers({'User-Agent': ['Tribler application tester']}), None)

        deferred.addCallback(_on_response)
        return deferred
    except:
        return fail()


class HTTPRequestManager(object):
    """
    This class manages requests to the Tribler core.
    """

    def get_token_balance(self):
        """
        Perform a request to the core to get the token balance.
        """
        def on_wallets_response(response):
            json_response = json.loads(response)
            if "MB" not in json_response["wallets"]:
                return 0
            return json_response["wallets"]["MB"]["balance"]["available"]

        return http_get("http://localhost:8085/wallets").addCallback(on_wallets_response)

    def get_downloads(self):
        """
        Perform a request to the core to get the downloads
        """
        return http_get("http://localhost:8085/downloads")

    def get_memory_history_core(self):
        """
        Perform a request to the core to get the memory usage history
        """
        return http_get("http://localhost:8085/debug/memory/history")

    def get_cpu_history_core(self):
        """
        Perform a request to the core to get the CPU usage history
        """
        return http_get("http://localhost:8085/debug/cpu/history")

    def get_state(self):
        """
        Get the current state of the Tribler instance
        """
        return http_get("http://localhost:8085/state")
