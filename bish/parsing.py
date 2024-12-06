from __future__ import annotations
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


@v_args(inline=True)
class MyTransformer(Transformer):
    def assignment(self, varname: str, value: LexerToken):
        return Assignment(varname, value)

    def command(self, command_name: LexerToken, *options):
        return Command(command_name.value, *options)

    def cond_eq(self, left: Any, right: Any):
        return IsEqualTo(left, right)

    def conditional(self, conditional):
        return conditional

    def env_var(self, varname: str):
        return EnvVar(varname[1:])

    def false(self, _):
        return False

    def float(self, n):
        return float(n)

    def if_(self, cond: Conditional, statement: Statement, else_: Statement):
        return If(cond, statement, else_)

    def int(self, n):
        return int(n)

    def nested_conditional(self, cond: Conditional):
        return NestedConditional(cond)

    def null(self, _):
        return None

    def option(self, option):
        """Return the option value, instead of a lexer token"""
        return option

    def statement(self, statement):
        """Return the statement value, instead of a lexer token"""
        return statement

    def statement_block(self, *statements):
        return StatementBlock(*statements)

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


class Statement(Token):
    pass


class Conditional(Token, ABC):
    @abstractmethod
    def eval(self, env: EnvironmentVarHolder) -> bool:
        pass


class NestedConditional(Conditional):
    def __init__(self, conditional: Conditional):
        self.conditional = conditional

    def eval(self, env: EnvironmentVarHolder) -> bool:
        return self.conditional.eval(env)


class If(Token):
    def __init__(self, conditional: Conditional, statement: Statement, else_: Token = None):
        self.conditional = conditional
        self.statement = statement
        self.else_ = else_

    def eval(self, env: EnvironmentVarHolder):
        if self.conditional.eval(env):
            self.statement.eval(env)
        elif self.else_:
            self.else_.eval(env)


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


class StatementBlock(Token):
    def __init__(self, *statements: Statement):
        self.statements = statements

    def eval(self, env: EnvironmentVarHolder):
        for statement in self.statements:
            statement.eval(env)


parser_options = {"parser": "lalr", "transformer": MyTransformer()}
parser = Lark.open("spec.lark", rel_to=__file__, **parser_options)
del parser_options["transformer"]
parser_without_transformer = Lark.open("spec.lark", rel_to=__file__, **parser_options)
