from pathlib import Path

import pytest
from ruamel.yaml import YAML

from turtleshell.parsing import parser_without_transformer as parser

yaml = YAML(typ="safe")

FIXTURES_DIR = Path(__file__).parent / "fixtures/parsing"

paths = sorted(list(FIXTURES_DIR.glob("*.yml")))


@pytest.mark.parametrize(("path"), paths, ids=[p.stem for p in paths])
def test_scalar(path: Path):
    test = yaml.load(path.read_text())
    tree = parser.parse(test["input"])
    assert tree.pretty(indent_str="  ").replace("\t", "  ").strip() == test["result"].strip()


@pytest.mark.parametrize(
    ("operator", "assignment_name"),
    [
        ("=", "EQUAL"),
        ("+=", "PLU_EQUAL"),
        ("-=", "MIN_EQUAL"),
        ("*=", "MUL_EQUAL"),
        ("/=", "DIV_EQUAL"),
    ],
    ids=["equals", "plus-equals", "minus-equals", "times-equals", "divide-equals"],
)
def test_assignments(operator: str, assignment_name: str):
    string = f"x {operator} 10"
    print(string)
    tree = parser.parse(string)
    # Hieracrchy is 'start' -> 'statement' -> 'assignment' -> [NAME, OP_NAME, VAL_TREE]'
    assert tree.children[0].children[0].children[1].type == assignment_name
