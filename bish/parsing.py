from abc import ABC, abstractmethod
import pathlib
from typing import Any
import subprocess

from lark import Lark, Transformer, v_args
from lark.lexer import Token as LexerToken

from bish.datatypes import CommandResult, Path
from bish.errors import CommandNotFound
from bish.variables import EnvironmentVarHolder
import bish.util


class MyTransformer(Transformer):
    @v_args(inline=True)
    def assignment(self, varname: str, value: LexerToken):
        return Assignment(varname, value)

    @v_args(inline=True)
    def command(self, command_name: LexerToken, options: list = []):
        return Command(command_name.value, *options)

    @v_args(inline=True)
    def env_var(self, varname: str):
        return EnvVar(varname[1:])

    def false(self, _):
        return False

    @v_args(inline=True)
    def float(self, n):
        return float(n)

    @v_args(inline=True)
    def int(self, n):
        return int(n)

    def null(self, _):
        return None

    def option(self, option):
        """Return the option value, instead of a lexer token"""
        return option

    def statement(self, statement):
        """Return the statement value, instead of a lexer token"""
        return statement

    @v_args(inline=True)
    def string(self, s):
        return s[1:-1].replace('\\"', '"')

    def true(self):
        return True


class Token:
    @abstractmethod
    def eval(self, env: EnvironmentVarHolder):
        pass


class Assignment(Token):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

    def eval(self, env: EnvironmentVarHolder):
        value = self.value
        if isinstance(value, Token):
            value = value.eval(env)
        env[self.name] = value
        print(f"{self.name}, {value}")


class Statement(Token):
    pass


class Conditional(Token, ABC):
    @abstractmethod
    def eval(self, env: EnvironmentVarHolder) -> bool:
        pass


class If(Token):
    def __init__(self, conditional: Conditional, statement: Statement, else_: Token = None):
        self.conditional = conditional
        self.statement = statement
        self.else_ = else_

    def eval(self, env: EnvironmentVarHolder):
        if self.conditional.eval(env):
            self.statement.eval
        elif self.else_:
            self.else_.eval()


class IsEqualTo(Conditional):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def eval(self, env):
        x, y = self.x, self.y
        if isinstance(self.x, Token):
            x = x.eval(env)
        if isinstance(y, Token):
            y = y.eval(env)
        return x == y


class EnvVar(Token):
    def __init__(self, name):
        self.name = name

    def eval(self, env: EnvironmentVarHolder) -> str:
        return env.get(self.name)


class Command(Statement):
    def __init__(self, name: str, *options: str):
        self.name = name
        self.options = options

    def eval(self, env: EnvironmentVarHolder):
        if cmd := bish.util.get_builtin(self.name):
            options = []
            for option in self.options:
                if isinstance(option, Token):
                    option = option.eval(env)
                options.append(option)
            return cmd().run(*options)

        return CommandResult.from_process(
            subprocess.run([env.get_executable(self.name)] + list(self.options))
        )

    def get_executable(self, name: str, env: EnvironmentVarHolder) -> pathlib.Path | None:
        for path in env["PATH"]:
            path = Path(path)
            if not path.value.exists():
                continue
            for item in path.value.iterdir():
                if item.stem == name and bish.util.is_executable(item):
                    return item
        # Else, raise an error because we didn't find an executable with that name
        raise CommandNotFound(name)


parser_options = {"parser": "lalr", "transformer": MyTransformer()}
parser = Lark.open("spec.lark", rel_to=__file__, **parser_options)
del parser_options["transformer"]
parser_without_transformer = Lark.open("spec.lark", rel_to=__file__, **parser_options)
