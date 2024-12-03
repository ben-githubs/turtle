import os
import inspect
from pathlib import Path
import platform

import bish.builtins

_BUILTINS = {}


def is_executable(fname: Path):
    return os.access(fname, os.X_OK)


def get_os_path():
    """Returns all the directories currently set as the OS path. Note that this function looks as
    the env var as set by the parent process running the shell. It doesn't asjust to changes made to
    bish's PATH variable."""
    pathstr = os.environ["PATH"]
    plat = platform.system()
    if plat == "Windows":
        pathlist = pathstr.split(";")
    elif plat in ("Darwin", "Linux"):
        pathlist = pathstr.split(":")
    return pathlist


def get_builtin(name: str) -> bish.builtins.Command | None:
    # Lazily build BUILTINS map
    if not _BUILTINS:
        for _, member in inspect.getmembers(bish.builtins):
            if inspect.isclass(member) and issubclass(member, bish.builtins.Command):
                _BUILTINS[member.name] = member
    return _BUILTINS.get(name)  # Return None if no builtin has this name
