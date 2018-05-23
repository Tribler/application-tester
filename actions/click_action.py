from action import Action


class ClickAction(Action):
    """
    This action clicks on an object in the GUI.
    """

    def __init__(self, click_obj_name, left_button=True):
        super(ClickAction, self).__init__()
        self.click_obj_name = click_obj_name
        self.left_button = left_button

    def action_code(self):
        button_spec = "LeftButton" if self.left_button else "RightButton"
        return "QTest.mouseClick(%s, Qt.%s)" % (self.click_obj_name, button_spec)

    def required_imports(self):
        return ["from PyQt5.QtTest import QTest", "from PyQt5.QtCore import Qt"]
