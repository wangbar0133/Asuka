"""Asuka orchestrator tests: error isolation and path validation."""
import shutil
from pathlib import Path

import pytest

from core.asuka import Asuka

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"

GARBAGE = "this is not solidity {{{ !!!"


@pytest.fixture
def mixed_dir(tmp_path):
    """A folder with one broken and one clean solidity file."""
    (tmp_path / "broken.sol").write_text(GARBAGE)
    shutil.copy(TEST_DATA / "reentrancy.sol", tmp_path / "clean.sol")
    return tmp_path


def test_scan_isolates_broken_files(mixed_dir):
    asuka = Asuka(_root=str(mixed_dir))
    asuka.scan()

    # the broken file is reported, not fatal
    assert len(asuka.errors) == 1
    assert "broken.sol" in asuka.errors[0]
    assert "Parse file failed" in asuka.errors[0]

    # the clean file still produced its full findings: 2x s101 + 3x s107
    assert asuka.vul_count() == 5


def test_vul_count_counts_from_vul_table(mixed_dir):
    asuka = Asuka(_root=str(mixed_dir))
    asuka.scan()
    assert asuka.vul_count() == asuka.vulTable.vul_count()


def test_path_not_found_raises(tmp_path):
    with pytest.raises(ValueError, match="Path not found"):
        Asuka(_root=str(tmp_path / "nope"))


def test_empty_sol_file_raises(tmp_path):
    empty = tmp_path / "empty.sol"
    empty.write_text("")
    with pytest.raises(ValueError, match="Invalid or empty solidity file"):
        Asuka(_root=str(empty))


def test_non_sol_file_raises(tmp_path):
    other = tmp_path / "contract.js"
    other.write_text("function f() {}")
    with pytest.raises(ValueError, match="Not a solidity file"):
        Asuka(_root=str(other))
