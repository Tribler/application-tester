from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.custom_action import CustomAction
from actions.page_action import PageAction
from actions.wait_action import WaitAction


class ChangeDownloadFilesAction(ActionSequence):
    """
    This action will include or exclude the file of a random download.
    """

    def __init__(self):
        super(ChangeDownloadFilesAction, self).__init__()

        self.add_action(PageAction('downloads'))
        self.add_action(WaitAction(1000))
        self.add_action(CustomAction("""if not window.downloads_page.downloads or len(window.downloads_page.downloads['downloads']) == 0:
    exit_script()
        """))
        self.add_action(ClickAction('window.downloads_list.topLevelItem(randint(0, len(window.downloads_page.download_widgets.keys()) - 1)).progress_slider'))
        self.add_action(WaitAction(2000))
        self.add_action(CustomAction('window.download_details_widget.setCurrentIndex(1)'))
        self.add_action(WaitAction(2000))
        self.add_action(CustomAction("""if window.download_files_list.topLevelItemCount() == 0:
    exit_script()
        """))
        self.add_action(CustomAction("item = window.download_files_list.topLevelItem(randint(0, window.download_files_list.topLevelItemCount() - 1))"))
        self.add_action(CustomAction("""if item.file_info['included']:
    window.download_details_widget.on_files_excluded([item.file_info])
else:
    window.download_details_widget.on_files_included([item.file_info])
        """))

    def required_imports(self):
        return ["from random import randint"]
