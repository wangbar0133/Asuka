from pathlib import Path

import pytest

from ast_scanner.ast_scanner import Scanner
from solidity_antlr4_parser.parser import objectify, parse_file

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def make_scanner(path: Path) -> Scanner:
    """Parse a .sol file and build its Scanner."""
    source_unit = parse_file(str(path), loc=True, strict=True)
    source_unit_object = objectify(source_unit, str(path))
    return Scanner(source_unit_object)


@pytest.fixture(scope="session")
def scan_file():
    """Parse a test_data file once per session and return its Scanner.

    Detectors are pure functions of the Scanner, so every test can
    reuse the same cached instance.
    """
    cache = {}

    def _scan(name: str) -> Scanner:
        if name not in cache:
            cache[name] = make_scanner(TEST_DATA / name)
        return cache[name]

    return _scan


@pytest.fixture(scope="session")
def scan_fixture():
    """Same as scan_file, for the targeted fixtures in tests/fixtures/.

    These fixtures exercise specific scanner/detector branches and are
    NOT part of the EXPECTED baseline matrix in test_detectors.py.
    """
    cache = {}

    def _scan(name: str) -> Scanner:
        if name not in cache:
            cache[name] = make_scanner(FIXTURES / name)
        return cache[name]

    return _scan
