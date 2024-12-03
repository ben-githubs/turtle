from abc import ABC, abstractmethod
import argparse
import os
from pathlib import Path
from typing import Any, Callable

from bish.datatypes import CommandResult
from bish.errors import ArgumentError

_BUILTINS = {}


class Command(ABC):
    def __init__(self):
        self.setup_parser()

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
        parser = argparse.ArgumentParser(prog=self.name, description="Print output to the console")
        parser.add_argument("string")
        parser.add_argument(
            "-n",
            dest="trailing_newline",
            action="store_false",
            default=True,
            help="do not output the trailing newline",
        )
        parser.add_argument(
            "-e",
            dest="enable_escapes",
            action="store_true",
            help="enable interpretation of backslash escapes",
        )
        parser.add_argument(
            "-E",
            dest="enable_escapes",
            action="store_false",
            help="disable interpretation of backslash escapes (default)",
        )
        self.parser = parser

    def run(self, *args: str) -> None:
        parsed = self.parser.parse_args(args)
        line_ending = "\n" if parsed.trailing_newline else ""
        print(parsed.string, end=line_ending)


class CWD(Command):
    name = "cwd"

    def setup_parser(self):
        # parser = argparse.ArgumentParser(
        #     prog="cwd",
        #     description="print the name of the current/working directory",
        # )
        # parser.add_argument(
        #     "-P", "--physical", dest="allow_symlinks", action="store_false", default=True
        # )
        # self.parser = parser
        self.parser = ArgParser()
        self.parser.add_argument(ArgFlag("allow_symlinks", store_true=False), "-P", "--physical")

    def run(self, *args: str) -> None:
        parsed = self.parser.parse_args(*args)
        out, err = "", ""
        try:
            out = cwd(parsed["allow_symlinks"])
        except Exception as e:
            err = str(e)
        return CommandResult(1 if err else 0, out, err)


class CD(Command):
    name = "cd"

    def setup_parser(self):
        parser = argparse.ArgumentParser(
            prog="cd",
            description="change the shell working directory",
        )
        parser.add_argument("dir")
        self.parser = parser

    def run(self, *args: str) -> None:
        parsed = self.parser.parse_args(args)
        err = ""
        try:
            d = Path(parsed.dir).expanduser().resolve()
            os.chdir(d)
        except FileNotFoundError as e:
            err = str(e)
        return CommandResult(1 if err else 0, "", err)


def cwd(allow_symlinks: bool = True) -> str:
    current_dir = Path(os.getcwd())
    if not allow_symlinks:
        current_dir = current_dir.resolve()
    return str(current_dir)


class CmdArg:
    def eval(self, arg: Any) -> dict:
        pass


class ArgPos(CmdArg):
    def __init__(self, name: str, dest: str = None, coerce: Callable = None):
        self.name = name
        self.dest = dest if dest else name
        self.coerce = coerce

    def eval(self, arg: Any) -> dict:
        return {self.dest: self.coerce(arg) if self.coerce is not None else arg}


class ArgFlag(CmdArg):
    """Represents a boolean flag that is either enabled or disabled when passed as an argument."""

    def __init__(self, dest: str, store_true: bool = True):
        self.dest = dest
        self.store_true = store_true

    def eval(self, is_present: bool) -> dict:
        # Also return 'true' if we want to store false, but it isn't present
        return {self.dest: is_present == self.store_true}


class ArgOpt(CmdArg):
    """Represents an option with 1 or more parameters."""

    def __init__(self, dest: str, nargs: int, coerce: Callable = None):
        self.dest = dest
        self.nargs = nargs
        self.coerce = coerce

    def eval(self, *args) -> dict:
        return [self.coerce(arg) if self.coerce else arg for arg in args]


class ArgParser:
    def __init__(self):
        self.args: list[CmdArg] = []
        self.kwargs: dict[str, CmdArg] = {}
        self.flags: list[ArgFlag] = []

    def add_argument(
        self,
        arg: CmdArg,
        *names: str,
    ):
        if isinstance(arg, ArgPos):
            self.pos_args.append(arg)
        else:
            if isinstance(arg, ArgFlag):
                self.flags.append(arg)
            for name in names:
                self.kwargs[name] = arg

    def is_arg(self, value: Any) -> bool:
        """Return if the value indicates a flag or the beginning of a set of options."""
        return isinstance(value, str) and value.startswith("-")

    def parse_args(self, *args: Any):
        argspace = {}

        # Get positional args first
        n_positional_args = len(self.args)
        for arg, val in zip(self.args, args[:n_positional_args]):
            argspace.update(arg.eval(val))

        # Do other args
        flags = set()
        arg_buffer = []
        arg: CmdArg = None
        idx = n_positional_args
        for value in args[idx:]:
            # There are exactly 3 posibilities:
            # 1) this is a flag, and can be handled entirely inside a single loop
            # 2) this is the beginning of an option
            # 3) this is a parameter for a previous option
            # We must handle these separately.

            # First, check if we are expecting a new argument definitioon (opt 1 or 2)
            if not arg and not self.is_arg(value):
                raise ArgumentError(f"Expected new argument; got {value}")

            # Otherwise, check if this is a new arg, and we need to wrap up our previous one
            if self.is_arg(value):
                if arg:
                    # Wrap up previous arg
                    argspace.update(arg.eval(*arg_buffer))

                # If the new arg is unrecognized
                arg_buffer = []
                arg = self.kwargs.get(value)
                if not arg:
                    raise ArgumentError(f"Unrecognized arg '{value}'")

                # If the new arg is a flag
                if isinstance(arg, ArgFlag):
                    flags.add(arg)
                    arg = None

                # Else, continue to next value
                continue

            # Lastly, if this is a parameter for the current argument
            arg_buffer.append(value)

        # At the end of the loop, if there's anything left in the arg buffer, we shoudl evaluate it
        if arg:
            argspace.update(arg.eval(*arg_buffer))

        # Lastly, evaluate any flags
        for flag in self.flags:
            argspace.update(flag.eval(flag in flags))

        return argspace
