import logging

from twisted.internet import protocol
from twisted.internet.defer import Deferred


class TriblerCodeClient(protocol.Protocol):

    def __init__(self):
        self.buffer = ''

    def connectionMade(self):
        self.factory.connect_deferred.callback(self)

    def dataReceived(self, data):
        """
        We received some data from Tribler. Parse it and handle it.
        """
        self.buffer = ''
        for line in data.split('\n'):
            if not line.startswith('result') and not line.startswith('crash'):
                self.buffer += line
            else:
                self.process_response(self.buffer)
                self.buffer = line

        self.process_response(self.buffer)

    def process_response(self, data):
        if data.startswith('result'):
            parts = data.split(' ')
            if len(parts) != 3:
                return
            result_value = parts[1].decode('base64')
            task_id = parts[2]
            self.factory.executor.on_task_result(task_id, result_value)
        elif data.startswith('crash'):
            parts = data.split(' ')
            if len(parts) != 2:
                return
            traceback = parts[1].decode('base64')
            self.factory.executor.on_tribler_crash(traceback)

    def run_code(self, code, task_id):
        self.transport.write("%s %s\n" % (code, task_id))


class TriblerCodeClientFactory(protocol.ClientFactory):
    protocol = TriblerCodeClient

    def __init__(self, executor):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.executor = executor
        self.connect_deferred = Deferred()
        self.connect_deferred.addCallback(self.executor.on_socket_ready)

    def clientConnectionFailed(self, connector, reason):
        self._logger.warning("Tribler code socket connection failed: %s", reason)

    def clientConnectionLost(self, connector, reason):
        self._logger.warning("Tribler code socket connection lost: %s", reason)
