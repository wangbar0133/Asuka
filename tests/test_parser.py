"""Strict-mode parsing tests for the ANTLR wrapper."""
from pathlib import Path

import pytest

from solidity_antlr4_parser.parser import parse

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"

GARBAGE = "this is not solidity {{{ !!!"


def test_non_strict_parse_tolerates_garbage():
    """Default mode keeps the historical error-tolerant behaviour."""
    tree = parse(GARBAGE)
    assert tree is not None


def test_strict_parse_rejects_garbage():
    with pytest.raises(SyntaxError, match="syntax error"):
        parse(GARBAGE, strict=True)


def test_strict_parse_accepts_valid_source():
    tree = parse("contract C { function f() public {} }", strict=True)
    assert tree is not None


def test_strict_error_message_names_the_file(tmp_path):
    bad = tmp_path / "bad.sol"
    bad.write_text(GARBAGE)
    with pytest.raises(SyntaxError, match="bad.sol"):
        parse(bad.read_text(), strict=True, path=str(bad))


def test_all_test_data_files_are_strict_clean():
    """Guards test fixtures against syntax typos.

    tx_origin.sol once carried a tolerated missing semicolon; with strict
    scanning enabled in the Asuka core, any fixture typo would now fail
    the whole scan, so fixtures must stay strictly parseable.
    """
    files = sorted(TEST_DATA.glob("*.sol"))
    assert len(files) == 10
    for sol in files:
        parse(sol.read_text(), strict=True, path=str(sol))
