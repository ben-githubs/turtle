import argparse
import os
from pathlib import Path
from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self):
        self.parser = self.setup_parser()

    @property
    @abstractmethod
    def name() -> str:
        pass


    @abstractmethod
    def run(*args, **kwargs):
        pass


    @abstractmethod
    def setup_parser(self):
        pass


class Print(Command):
    name = "print"

    def setup_parser(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            descrption="Print output to the console"
        )
        parser.add_argument("string")
        parser.add_argument(
            "-n",
            dest="trailing_newline",
            action="store_false",
            default=True,
            help="do not output the trailing newline"
        )
        parser.add_argument(
            "-e",
            dest="enable_escapes",
            action="store_true",
            help="enable interpretation of backslash escapes"
        )
        parser.add_argument(
            "-E",
            dest="enable_escapes",
            action="store_false",
            help="disable interpretation of backslash escapes (default)"
        )
        self.parser = parser
    

    def run(self, args: list[str]) -> None:
        parsed = self.parser.parse_args(args)
        line_ending = "\n" if parsed.trailing_newline else ""
        print(parsed.string, end=line_ending)


class CWD(Command):
    name = "cwd"

    def setup_parser(self):
        parser = argparse.ArgumentParser(
            prog="cwd",
            description="print the name of the current/working directory",
        )
        parser.add_argument(
            "-P",
            "--physical",
            dest="allow_symlinks",
            action="store_false",
            default=True
        )
        self.parser = parser
    
    def run(self, args: list[str]) -> None:
        parsed = self.parser.parse_args(args)
        print("")


def cwd(allow_symlinks: bool = True) -> str:
    return os.getcwd()