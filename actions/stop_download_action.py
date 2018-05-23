from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.page_action import PageAction
from actions.wait_action import WaitAction


class StopRandomDownloadAction(ActionSequence):
    """
    This action will stop a random download.
    """

    def __init__(self):
        super(StopRandomDownloadAction, self).__init__()

        self.add_action(PageAction('downloads'))
        self.add_action(WaitAction(1000))
        self.add_action(ClickAction('window.downloads_list.topLevelItem(randint(0, len(window.downloads_page.download_widgets.keys()) - 1)).progress_slider'))
        self.add_action(ClickAction('window.remove_download_button'))
        self.add_action(ClickAction('window.downloads_page.dialog.buttons[1]'))

    def required_imports(self):
        return ["from random import randint"]
