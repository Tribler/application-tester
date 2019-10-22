from __future__ import absolute_import

from action import Action


class CustomAction(Action):
    """
    This action allows programmers to define their own actions with custom code.
    """

    def __init__(self, code):
        super(CustomAction, self).__init__()
        self.code = code

    def action_code(self):
        return self.code

    def required_imports(self):
        return []
