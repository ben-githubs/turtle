from pathlib import Path

import pytest
from ruamel.yaml import YAML

from bish.parsing import parser_without_transformer as parser

yaml = YAML(typ="safe")

FIXTURES_DIR = Path(__file__).parent / "fixtures/parsing"

paths = sorted(list(FIXTURES_DIR.glob("*.yml")))


@pytest.mark.parametrize(("path"), paths, ids=[p.stem for p in paths])
def test_scalar(path: Path):
    test = yaml.load(path.read_text())
    tree = parser.parse(test["input"])
    # breakpoint()
    assert tree.pretty(indent_str="  ").replace("\t", "  ").strip() == test["result"].strip()