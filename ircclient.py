from twisted.internet import protocol, reactor
from twisted.words.protocols import irc
from twisted.words.protocols.irc import lowQuote


class Bot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % self.nickname

    def joined(self, channel):
        print "Joined %s." % channel

    def privmsg(self, user, channel, message):
        print message


class BotFactory(protocol.ClientFactory):

    def __init__(self, channel, nickname='twistedbot12389654'):
        self.channel = channel
        self.nickname = nickname
        self.bot = Bot()

    def buildProtocol(self, addr):
        self.bot.factory = self
        return self.bot

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reason: %s" % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed. Reason: %s" % reason

    def send_channel_message(self, message):
        self.bot.msg(self.channel, message)


class IRCManager(object):
    """
    This class manages the IRC connection with the Freenode server.
    """

    def __init__(self, nickname):
        self.irc = BotFactory('#triblerapptester', nickname=nickname)

    def start(self):
        reactor.connectTCP('irc.freenode.net', 6667, self.irc)
