from pathlib import Path

import pytest

from ast_scanner.ast_scanner import Scanner
from solidity_antlr4_parser.parser import objectify, parse_file

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"


@pytest.fixture(scope="session")
def scan_file():
    """Parse a .sol file once per session and return its Scanner.

    Detectors are pure functions of the Scanner, so every test can
    reuse the same cached instance.
    """
    cache = {}

    def _scan(name: str) -> Scanner:
        if name not in cache:
            path = TEST_DATA / name
            source_unit = parse_file(str(path), loc=True)
            source_unit_object = objectify(source_unit, str(path))
            cache[name] = Scanner(source_unit_object)
        return cache[name]

    return _scan
