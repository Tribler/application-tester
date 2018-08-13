from action import Action


class ShutdownAction(Action):
    """
    This action shuts down Tribler.
    """
    def action_code(self):
        return "window.close_tribler()"

    def required_imports(self):
        return []
