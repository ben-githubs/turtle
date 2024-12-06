"""Main program for Ben's Incredible SHell."""

import inspect
import os
import pathlib
import platform
import re

import colorama
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from turtleshell import builtins
from turtleshell.errors import CommandNotFound
from turtleshell.datatypes import Path
from turtleshell.variables import EnvironmentVarHolder
from turtleshell.parsing import parser
from turtleshell.evaluate import evaluate
from turtleshell.multilines import is_complete, concatenate_incomplete_lines

VERSION = "0.0.1"

colorama.init()

ENV_VARS = EnvironmentVarHolder()

BUILTINS: dict[str, builtins.Command] = {}


def load_builtins():
    members = inspect.getmembers()
    for member in members:
        if inspect.issubclass(member, builtins.Command):
            cmd = member()
            BUILTINS[cmd.name] = cmd


def get_histfile() -> pathlib.Path:
    """Returns the path to the history file."""
    if histfile := ENV_VARS.get("HISTFILE"):
        if isinstance(histfile, Path):
            return histfile.value.expanduser().resolve()
    # Else, return a default value
    return pathlib.Path("~/.turtle_history").expanduser().resolve()


def main():
    print("🐢 turtle version " + VERSION)
    if platform.system() not in ("Windows", "Linux", "Darwin"):
        print(f"Unsupported platform: '{platform.system()}'. Must exit now.")
        exit(1)


    # Initialize prompt history
    histfile = get_histfile()
    with histfile.open("r") as f:
        history = [line.strip() for line in f.readlines()]
    # Only keep the last 100 commands
    if len(history) > 100:
        history = history[-100:]
        with histfile.open("w") as f:
            f.write(os.linesep.join(history))
    
    prompt_session = PromptSession(history=InMemoryHistory(history_strings=history))

    while True:
        prompt1: str = ENV_VARS["PROMPT1"]
        env_vars = set(m for m in re.findall(r"\$\w+", prompt1))
        for env_var in env_vars:
            prompt1 = prompt1.replace(env_var, str(ENV_VARS.get(env_var[1:], "")))

        input_ = [prompt_session.prompt(prompt1).strip()]
        while not is_complete(" ".join(input_)):
            input_.append(prompt_session.prompt(ENV_VARS["PROMPT2"]))

        input_ = concatenate_incomplete_lines(input_)

        # Log input to history file
        histfile = get_histfile()
        with histfile.open("a") as f:
            f.write(input_ + os.linesep)

        # If nothing is entered, just move to next loop
        if not input_:
            continue

        if input_ == "exit":
            break

        tree = parser.parse(input_)
        try:
            for statement in tree.children:
                evaluate(statement, ENV_VARS)
        except CommandNotFound as e:
            print(f"{e}: command not found")


if __name__ == "__main__":
    main()
