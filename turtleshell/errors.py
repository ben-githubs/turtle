class ShellError(BaseException):
    pass


class InvalidAssignment(ShellError):
    pass


class CommandNotFound(ShellError):
    def __init__(self, name):
        super().__init__(name)


class ArgumentError(ShellError):
    """We had issues while parsing the arguments for a command."""
