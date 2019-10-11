from __future__ import absolute_import

from six.moves import xrange

from action_sequence import ActionSequence
from actions.page_action import PageAction
from actions.scroll_action import RandomScrollAction
from actions.wait_action import WaitAction


class BrowseDiscoveredAction(ActionSequence):
    """
    This action scrolls through the discovered torrents in Tribler.
    """

    def __init__(self):
        super(BrowseDiscoveredAction, self).__init__()

        self.add_action(PageAction('discovered'))
        for _ in range(0, 10):
            self.add_action(RandomScrollAction("window.discovered_channels_list"))
            self.add_action(WaitAction(300))
