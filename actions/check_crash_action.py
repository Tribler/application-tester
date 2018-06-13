from action import Action


class CheckCrashAction(Action):
    """
    This action checks whether Tribler has crashed.
    """

    def __init__(self):
        super(CheckCrashAction, self).__init__()

    def action_code(self):
        return """if window.error_dialog:
    return_value = window.error_dialog.error_text_edit.toPlainText()
        """

    def required_imports(self):
        return []
