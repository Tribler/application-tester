from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.custom_action import CustomAction
from actions.page_action import PageAction
from actions.wait_action import WaitAction


class SubscribeUnsubscribeAction(ActionSequence):
    """
    This action will subscribe/unsubscribe to/from a random channel in the list of discovered channels.
    """

    def __init__(self):
        super(SubscribeUnsubscribeAction, self).__init__()

        self.add_action(PageAction('discovered'))
        self.add_action(WaitAction(1000))
        self.add_action(CustomAction("""if window.discovered_channels_list.count() == 0:
    exit_script()
    """))
        self.add_action(ClickAction('window.discovered_channels_list.itemWidget(window.discovered_channels_list.item(randint(0, window.discovered_channels_list.count() - 1))).subscribe_button'))

    def required_imports(self):
        return ["from random import randint"]
