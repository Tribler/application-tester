from __future__ import absolute_import

from random import choice

from action_sequence import ActionSequence
from actions.click_action import ClickAction
from actions.custom_action import CustomAction
from actions.key_action import KeyAction
from actions.keys_action import KeysAction


class SearchAction(ActionSequence):
    """
    This action performs a search in Tribler.
    """

    def __init__(self, search_query):
        super(SearchAction, self).__init__()
        self.search_query = search_query

        # Add the actions to perform a search
        self.add_action(CustomAction("window.top_search_bar.setText('')"))
        self.add_action(ClickAction("window.top_search_bar"))
        self.add_action(KeysAction("window.top_search_bar", self.search_query, 200))
        self.add_action(KeyAction("window.top_search_bar", "Key_Enter"))


class RandomSearchAction(SearchAction):
    """
    This action performs a random search in Tribler.
    """
    SEARCH_KEYWORDS = ['search', 'vodo', 'eztv', 'big buck bunny', 'windows', 'debian', 'linux', '2012', 'pioneer',
                       'tribler', 'test', 'free music', 'free video', '2016', 'whatsapp', 'ebooks', 'race', 'funny']

    def __init__(self):
        super(RandomSearchAction, self).__init__(choice(self.SEARCH_KEYWORDS))
