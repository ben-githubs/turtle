import os
from pathlib import Path
import platform

def is_executable(fname: Path):
    return os.access(fname, os.X_OK)


def get_os_path():
    """ Returns all the directories currently set as the OS path. Note that this function looks as
    the env var as set by the parent process running the shell. It doesn't asjust to changes made to
    bish's PATH variable. """
    pathstr = os.environ["PATH"]
    plat = platform.system()
    if plat == "Windows":
        pathlist = pathstr.split(";")
    elif plat in ("Darwin", "Linux"):
        pathlist = pathstr.split(":")
    return pathlist
