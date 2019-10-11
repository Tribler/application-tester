from __future__ import absolute_import

from action_sequence import ActionSequence
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
        self.add_action(CustomAction("""if window.discovered_channels_list.model().rowCount() == 0:
    exit_script()
    """))

        self.add_action(CustomAction("""table_view = window.discovered_channels_list
random_row = randint(0, table_view.model().rowCount() - 1)
x = table_view.columnViewportPosition(0)
y = table_view.rowViewportPosition(random_row)
index = table_view.indexAt(QPoint(x, y))
table_view.on_subscribe_control_clicked(index)
        """))

    def required_imports(self):
        return ["from PyQt5.QtCore import QPoint", "from random import randint"]
