"""This handles how environment variables are.. well... handled."""

from collections.abc import MutableMapping
from datetime import datetime
import getpass
import os
import pathlib
import tempfile
from typing import Any

from bish.builtins import cwd
from bish.datatypes import DateTime, Path
from bish.errors import InvalidAssignment, CommandNotFound
import bish.util

CROSS_PLATFORM_MAPPINGS = {"nt": {"PROMPT": "B_PS1"}, "posix": {"PS1": "B_PS1"}}

# Mapping of read-only shell variables, and how to determine their values
SHELL_VARS = {
    "CWD": lambda: Path(cwd()),
    "DATE": lambda: DateTime(datetime.now()),
    "HOME": Path(pathlib.Path.home()),
    "HOST": os.uname().nodename,
    "OS": os.uname().sysname,
    "TMP": Path(tempfile.gettempdir()),
    "USER": getpass.getuser(),
}

# Some vars can be edited, but not deleted. We define the default value of those here.
DEFAULT_VALUES = {
    "PROMPT1": r"$USER@$HOST: $CWD $ ",  # Prompt string
    "RPROMPT1": "",  # Prints on right side of terminal when prompting for input
    "PROMPT2": "> ",  # Prompt for trailing input
    "PROMPT3": "#?",  # Don't remember what this does
    "PROMPT4": "+",  # For debug lines (do we even want this?)
    "PATH": bish.util.get_os_path(),
}


class EnvironmentVarHolder(MutableMapping):
    def __init__(self):
        self._data: dict[str, Any] = {}

    def get_executable(self, name: str) -> pathlib.Path | None:
        for path in self["PATH"]:
            path = Path(path)
            if not path.value.exists():
                continue
            for item in path.value.iterdir():
                if item.stem == name and bish.util.is_executable(item):
                    return item
        # Else, raise an error because we didn't find an executable with that name
        raise CommandNotFound(name)

    def __getitem__(self, key: str):
        # Handle special cases
        if val := SHELL_VARS.get(key):
            if callable(val):
                val = val()
            return val

        # Else, check the internal env var store
        return self._data.get(key) or DEFAULT_VALUES.get(key, "")

    def __setitem__(self, key: str, value):
        # Make sure this isn't a read-only variable
        if key in SHELL_VARS:
            raise InvalidAssignment(
                f"Shell variable '{key}' is read-only and cannot be written to."
            )

        # Special variables
        if mapped_key := CROSS_PLATFORM_MAPPINGS.get(os.name, {}).get(key):
            self[mapped_key] = value
        else:
            self._data[key] = value

    def __delitem__(self, key: str):
        # Make sure this isn't a read-only variable
        if key in SHELL_VARS:
            raise InvalidAssignment(
                f"Shell variable '{key}' is read-only and cannot be written to."
            )

        # Else, just delete it
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()
