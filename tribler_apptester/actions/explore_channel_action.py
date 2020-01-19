from __future__ import absolute_import

from tribler_apptester.action_sequence import ActionSequence
from tribler_apptester.actions.click_action import ClickAction, RandomTableViewClickAction
from tribler_apptester.actions.custom_action import CustomAction
from tribler_apptester.actions.page_action import PageAction
from tribler_apptester.actions.select_action import TableViewRandomSelectAction
from tribler_apptester.actions.wait_action import WaitAction


class ExploreChannelAction(ActionSequence):
    """
    This action will 'explore' a discovered channel.
    """

    def __init__(self):
        super(ExploreChannelAction, self).__init__()

        self.add_action(PageAction('discovered'))
        self.add_action(WaitAction(1000))
        self.add_action(CustomAction("""if window.discovered_channels_list.model().rowCount() == 0:
    exit_script()
        """))
        self.add_action(RandomTableViewClickAction('window.discovered_channels_list'))
        self.add_action(WaitAction(2500))

        # We now click a random torrent to initiate the torrent checker
        self.add_action(CustomAction("""if window.channel_page_container.content_table.model().rowCount() == 0:
    exit_script()
        """))

        self.add_action(TableViewRandomSelectAction('window.channel_page_container.content_table'))
        self.add_action(WaitAction(2000))
        self.add_action(ClickAction('window.channel_back_button'))

    def required_imports(self):
        return ["from random import randint"]
