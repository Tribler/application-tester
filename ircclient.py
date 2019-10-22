from __future__ import absolute_import

from twisted.internet import protocol, reactor
from twisted.words.protocols import irc


class Bot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print("Signed on as %s.", self.nickname)

    def joined(self, channel):
        print("Joined %s.", channel)

    def privmsg(self, user, channel, message):
        if message.startswith("!"):
            self.parse_command(message)

    def parse_command(self, message):
        parts = message.split(" ")
        if len(parts) != 2:
            return

        command = parts[0][1:]
        botname = parts[1]

        if botname != self.factory.nickname:
            return

        # This is a command for this bot
        if command == "status":
            self.msg(self.factory.channel, "crashed? %s, uptime: %d seconds" % (self.executor.tribler_crashed, self.executor.uptime))
        elif command == "balance":
            def on_token_balance(balance):
                self.msg(self.factory.channel, "balance: %d MB" % balance)

            self.executor.request_manager.get_token_balance().addCallback(on_token_balance)


class BotFactory(protocol.ClientFactory):

    def __init__(self, channel, executor, nickname='twistedbot12389654'):
        self.channel = channel
        self.nickname = nickname
        self.bot = Bot()
        self.bot.heartbeatInterval = 20
        self.bot.executor = executor

    def buildProtocol(self, addr):
        self.bot.factory = self
        return self.bot

    def clientConnectionLost(self, connector, reason):
        print("Connection lost. Reason: %s", reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed. Reason: %s", reason)

    def send_channel_message(self, message):
        self.bot.msg(self.channel, message)


class IRCManager(object):
    """
    This class manages the IRC connection with the Freenode server.
    """

    def __init__(self, executor, nickname):
        self.irc = BotFactory('#triblerapptester', executor, nickname=nickname)

    def start(self):
        reactor.connectTCP('irc.freenode.net', 6667, self.irc)
