from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.custom_action import CustomAction
from actions.page_action import PageAction
from actions.wait_action import WaitAction


class StartVODAction(ActionSequence):
    """
    This action start a VOD stream of a random, existing download.
    """

    def __init__(self):
        super(StartVODAction, self).__init__()

        self.add_action(PageAction('downloads'))
        self.add_action(WaitAction(1000))
        self.add_action(CustomAction("""if len(window.downloads_page.downloads['downloads']) == 0:
    exit_script()
        """))
        self.add_action(ClickAction('window.downloads_list.topLevelItem(randint(0, len(window.downloads_page.download_widgets.keys()) - 1)).progress_slider'))
        self.add_action(WaitAction(2000))
        self.add_action(ClickAction('window.play_download_button'))

    def required_imports(self):
        return ["from random import randint"]
