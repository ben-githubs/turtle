"""Main program for Ben's Incredible SHell."""

import inspect
import platform
import re

import colorama

from bish import builtins
from bish.errors import CommandNotFound
from bish.variables import EnvironmentVarHolder
from bish.parsing import parser
from bish.evaluate import evaluate
from bish.multilines import is_complete, concatenate_incomplete_lines

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


def main():
    print("bish version " + VERSION)
    if platform.system() not in ("Windows", "Linux", "Darwin"):
        print(f"Unsupported platform: '{platform.system()}'. Must exit now.")
        exit(1)

    while True:
        prompt1: str = ENV_VARS["PROMPT1"]
        env_vars = set(m for m in re.findall(r"\$\w+", prompt1))
        for env_var in env_vars:
            prompt1 = prompt1.replace(env_var, str(ENV_VARS.get(env_var[1:], "")))

        input_ = [input(prompt1).strip()]
        while not is_complete(" ".join(input_)):
            input_.append(input(ENV_VARS["PROMPT2"]))
        
        input_ = concatenate_incomplete_lines(input_)


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
