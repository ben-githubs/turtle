from bish.parsing import Token
from bish.variables import EnvironmentVarHolder


def evaluate(token: Token, env: EnvironmentVarHolder):
    result = token.eval(env)
    if result is not None and str(result):
        print(result)
