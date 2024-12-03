from abc import ABC


class Command(ABC):
    """Represents a command that can be run."""

    def __init__(self, help_text: str = ""):
        pass
