"""Define some data types, mostly wrappers for Python datatypes."""

from datetime import datetime
import pathlib
import subprocess
import time


class DataType:
    def __init__(self, value):
        self.value = value
    

    def __str__(self) -> str:
        return str(self.value)


class Integer(DataType):
    pass


class DateTime(DataType):
    
    def __init__(self, value: datetime):
        self.value = value
    

    def iso(self) -> str:
        return self.value.isoformat()
    

    def rfc(self) -> str:
        return self.value.strftime("%a, %-d %b %Y %H:%M:%S")
    

    def unix(self) -> Integer:
        return Integer(round(time.mktime(self.value.timetuple())))
    

    def ctime(self) -> str:
        return self.value.ctime()
    

    def format(self, fmtstr: str) -> str:
        return self.value.strftime(fmtstr)


    def __str__(self) -> str:
        return str(self.unix)

class Path(DataType):
    def __init__(self, value: str | pathlib.Path):
        if not isinstance(value, pathlib.Path):
            value = pathlib.Path(value)
        self.value = value
    

    def parent(self):
        return self.value.parent
    

    def stem(self):
        return self.value.stem
    

    def name(self):
        return self.value.name


class CommandResult(DataType):
    def __init__(self, proc: subprocess.CompletedProcess):
        self._proc = proc
    

    @property
    def code(self):
        return self._proc.returncode
    

    @property
    def stdout(self):
        return self._proc.stdout
    

    @property
    def stderr(self):
        return self._proc.stderr


    def __str__(self):
        s = self._proc.stdout
        if s is None:
            return ""
        if isinstance(s, bytes):
            return s.decode('utf-8')
        return str(s)
    

    def __bool__(self):
        return self.proc.returncode == 0