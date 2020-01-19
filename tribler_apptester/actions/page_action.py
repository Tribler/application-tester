from __future__ import absolute_import

from random import choice

from tribler_apptester.actions.click_action import ClickSequenceAction


class PageAction(ClickSequenceAction):
    """
    This action goes to a specific page in Tribler.
    """
    BUTTONS_TO_PAGES = {
        'home': ['window.left_menu_button_home'],
        'discovered': ['window.left_menu_button_discovered'],
        'downloads': ['window.left_menu_button_downloads'],
        'my_channel': ['window.left_menu_button_my_channel'],
        'search': ['window.left_menu_button_search'],
        'subscriptions': ['window.left_menu_button_subscriptions'],
        'video_player': ['window.left_menu_button_video_player'],
        'token_balance': ['window.token_balance_widget'],
        'settings': ['window.settings_button'],
        'market': ['window.token_balance_widget', 'window.trade_button'],
        'token_mining': ['window.token_balance_widget', 'window.mine_button'],
    }

    def __init__(self, page_name):
        super(PageAction, self).__init__(self.BUTTONS_TO_PAGES[page_name])


class RandomPageAction(PageAction):
    """
    This action goes to a random page in Tribler.
    """

    def __init__(self):
        rand_page = choice(list(self.BUTTONS_TO_PAGES.keys()))
        super(RandomPageAction, self).__init__(rand_page)
