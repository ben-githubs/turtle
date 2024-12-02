"""Main program for Ben's Incredible SHell."""

import getpass
import inspect
import os
from pathlib import Path
import platform

import colorama
import termcolor

from bish import builtins
from bish.errors import CommandNotFound
from bish.variables import EnvironmentVarHolder
from bish.parsing import parser
from bish.evaluate import evaluate

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
        input_ = input(ENV_VARS["PROMPT1"]).strip()
        
        # If nothing is entered, just move to next loop
        if not input_:
            continue
            
        if input_ == "exit":
            break

        tree = parser.parse(input_)
        try:
            for statement in tree.children:
                evaluate(statement[0], ENV_VARS)
        except CommandNotFound as e:
            print(f"{e}: command not found")

if __name__ == "__main__":
    main()