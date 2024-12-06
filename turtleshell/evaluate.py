from turtleshell.parsing import Token
from turtleshell.variables import EnvironmentVarHolder


def evaluate(token: Token, env: EnvironmentVarHolder):
    result = token.eval(env)
    if result is not None and str(result):
        print(result)
