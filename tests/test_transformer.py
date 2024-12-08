import pytest

import turtleshell.parsing as parsing


@pytest.mark.parametrize(
    ("operator", "new_val"), [("=", 2), ("+=", 12), ("-=", 8), ("*=", 20), ("/=", 5)]
)
def test_assignment(operator: str, new_val: int):
    """Performs a test that x (with assumed value of 10), when assigned 2, returns the appropriate
    value."""
    string = f"x {operator} 2"
    token = parsing.parser.parse(string).children[0]
    assert token.func(10, 2) == new_val
