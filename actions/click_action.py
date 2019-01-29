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


class ClickSequenceAction(Action):
    """
    This action clicks on multiple object in the GUI.
    """

    def __init__(self, click_obj_names):
        super(ClickSequenceAction, self).__init__()
        self.click_obj_names = click_obj_names

    def action_code(self):
        code = ""
        for click_obj_name in self.click_obj_names:
            code += "QTest.mouseClick(%s, Qt.LeftButton)\n" % click_obj_name
            code += "QTest.qWait(1000)\n"

        return code

    def required_imports(self):
        return ["from PyQt5.QtTest import QTest", "from PyQt5.QtCore import Qt"]
