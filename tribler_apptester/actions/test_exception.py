from tribler_apptester.action import Action


class TestExceptionAction(Action):
    """
    This action deliberately makes an exception to test that Sentry correctly receives this error
    """

    def __init__(self):
        super(KeyAction, self).__init__()

    def action_code(self):
        return """
class TestException(Exception):
    pass
raise TestException('Test Tribler exception induced by Application Tester')
"""
