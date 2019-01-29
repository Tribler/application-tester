from random import choice

from actions.click_action import ClickAction


class PageAction(ClickAction):
    """
    This action goes to a specific page in Tribler.
    """
    BUTTONS_TO_PAGES = {
        'home': 'window.left_menu_button_home',
        'discovered': 'window.left_menu_button_discovered',
        'downloads': 'window.left_menu_button_downloads',
        'my_channel': 'window.left_menu_button_my_channel',
        'search': 'window.left_menu_button_search',
        'subscriptions': 'window.left_menu_button_subscriptions',
        'video_player': 'window.left_menu_button_video_player',
        'token_balance': 'window.token_balance_widget',
        'settings': 'window.settings_button'
    }

    def __init__(self, page_name):
        super(PageAction, self).__init__(self.BUTTONS_TO_PAGES[page_name], left_button=True)


class RandomPageAction(PageAction):
    """
    This action goes to a random page in Tribler.
    """

    def __init__(self):
        rand_page = choice(self.BUTTONS_TO_PAGES.keys())
        super(RandomPageAction, self).__init__(rand_page)
