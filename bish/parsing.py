from abc import ABC, abstractmethod
import subprocess

from lark import Lark, Transformer, v_args
from lark.tree import Branch
from lark.lexer import Token as LexerToken

from bish.datatypes import CommandResult
from bish.variables import EnvironmentVarHolder

class MyTransformer(Transformer):

    true = lambda self, _: True
    false = lambda self, _: False
    null = lambda self, _: None
    int = int
    float = float

    @v_args(inline=True)
    def string(self, s):
        return s[1:-1].replace('\\"', '"')
    
    def option(self, option):
        """ Return the option value, instead of a lexer token """
        return option
    
    def statement(self, statement):
        """ Return the statement value, instead of a lexer token """
        return statement

    @v_args(inline=True)
    def command(self, command_name: LexerToken, options: list = []):
        return Command(command_name.value, *options)


class Token():
    @abstractmethod
    def eval(self, env: EnvironmentVarHolder):
        pass


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


    def eval(self, env: EnvironmentVarHolder):
        return env.get(self.name)


class Command(Statement):
    def __init__(self, name: str, *options: str):
        self.name = name
        self.options = options
    

    def eval(self, env: EnvironmentVarHolder):
        return CommandResult(
            subprocess.run([env.get_executable(self.name)] + list(self.options))
        )




parser_options = {
    "parser": "lalr",
    "transformer": MyTransformer()
}
parser = Lark.open("spec.lark", rel_to=__file__, **parser_options)
del parser_options["transformer"]
parser_without_transformer = Lark.open("spec.lark", rel_to=__file__, **parser_options)