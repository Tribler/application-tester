from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.custom_action import CustomAction
from actions.page_action import PageAction
from actions.wait_action import WaitAction


class ExploreChannelAction(ActionSequence):
    """
    This action will 'explore' a discovered channel.
    """

    def __init__(self):
        super(ExploreChannelAction, self).__init__()

        self.add_action(PageAction('discovered'))
        self.add_action(WaitAction(1000))
        self.add_action(CustomAction("""if window.discovered_channels_list.count() == 0:
    exit_script()
        """))
        self.add_action(ClickAction('window.discovered_channels_list.itemWidget(window.discovered_channels_list.item(randint(0, window.discovered_channels_list.count() - 1)))'))
        self.add_action(WaitAction(2500))

        # We now click a random torrent to initiate the torrent checker
        self.add_action(CustomAction("""if window.channel_page_container.items_list.count() == 0:
    exit_script()
        """))
        self.add_action(ClickAction('window.channel_page_container.items_list.itemWidget(window.channel_page_container.items_list.item(randint(0, window.channel_page_container.items_list.count() - 1)))'))
        self.add_action(WaitAction(2000))
        self.add_action(ClickAction('window.channel_back_button'))

    def required_imports(self):
        return ["from random import randint"]
