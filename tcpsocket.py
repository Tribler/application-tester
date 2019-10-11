from __future__ import absolute_import

import logging
from base64 import b64decode

from twisted.internet import protocol
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure


class TriblerCodeClient(protocol.Protocol):

    def __init__(self):
        self.buffer = b''

    def connectionMade(self):
        self.factory.connect_deferred.callback(self)

    def dataReceived(self, data):
        """
        We received some data from Tribler. Parse it and handle it.
        """
        self.buffer = b''
        for line in data.split(b'\n'):
            if not line.startswith(b'result') and not line.startswith(b'crash'):
                self.buffer += line
            else:
                self.process_response(self.buffer)
                self.buffer = line

        self.process_response(self.buffer)

    def process_response(self, data):
        if data.startswith(b'result'):
            parts = data.split(b' ')
            if len(parts) != 3:
                return
            result_value = b64decode(parts[1])
            task_id = parts[2]
            self.factory.executor.on_task_result(task_id, result_value)
        elif data.startswith(b'crash'):
            parts = data.split(b' ')
            if len(parts) != 2:
                return
            traceback = b64decode(parts[1])
            self.factory.executor.on_tribler_crash(traceback)

    def run_code(self, code, task_id):
        self.transport.write(b"%s %s\n" % (code, task_id))


class TriblerCodeClientFactory(protocol.ClientFactory):
    protocol = TriblerCodeClient

    def __init__(self, executor):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.executor = executor
        self.connect_deferred = Deferred()
        self.connect_deferred.addCallbacks(self.executor.on_socket_ready, self.executor.on_socket_failed)

    def clientConnectionFailed(self, connector, reason):
        self._logger.warning("Tribler code socket connection failed: %s", reason)
        self.connect_deferred.errback(Failure(RuntimeError("Failed to connect to Tribler socket!")))

    def clientConnectionLost(self, connector, reason):
        self._logger.warning("Tribler code socket connection lost: %s", reason)
