from bish.parsing import Token
from bish.variables import EnvironmentVarHolder

def evaluate(token: Token, env: EnvironmentVarHolder):
    if s := str(token.eval(env)):
        print(s)