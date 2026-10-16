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


class TestIsSolFile:
    def test_valid_file(self, tmp_path):
        sol = tmp_path / "ok.sol"
        sol.write_text("contract C {}")
        asuka = Asuka.__new__(Asuka)
        assert asuka._is_sol_file(str(sol))

    def test_wrong_suffix(self, tmp_path):
        other = tmp_path / "ok.txt"
        other.write_text("contract C {}")
        asuka = Asuka.__new__(Asuka)
        assert not asuka._is_sol_file(str(other))

    def test_empty_file(self, tmp_path):
        sol = tmp_path / "empty.sol"
        sol.write_text("")
        asuka = Asuka.__new__(Asuka)
        assert not asuka._is_sol_file(str(sol))


def test_scan_file_in_process():
    """scan_file can be called directly, without the process pool.

    Runs the parse/scan/detect pipeline in-process so coverage sees it.
    """
    asuka = Asuka(_root=str(TEST_DATA / "reentrancy.sol"))
    vul_list = asuka.scan_file((str(TEST_DATA / "reentrancy.sol"), [101, 107]))
    assert [v.id for v in vul_list] == [101, 107]
    assert vul_list[0].vul_count() == 2  # int overflow
    assert vul_list[1].vul_count() == 3  # reentrancy


def test_scan_file_reports_parse_failure():
    asuka = Asuka.__new__(Asuka)
    with pytest.raises(RuntimeError, match="Parse file failed"):
        asuka.scan_file(("/nonexistent/bad.sol", [101]))


def test_address_input_uses_scraper(monkeypatch, tmp_path):
    """A valid address + chain + key resolves files through the scraper."""
    import core.asuka as asuka_module

    sol = tmp_path / "Token.sol"
    sol.write_text("contract Token {}")

    class StubScraper:
        def __init__(self, chainType, apiKey):
            assert chainType == "ETH"
            assert apiKey == "test-key"

        def get_source_code(self, address):
            return str(tmp_path)

    monkeypatch.setattr(asuka_module, "Scraper", StubScraper)
    asuka = Asuka(
        _root="0x" + "ab" * 20, _chainType="ETH", _apiKey="test-key"
    )
    assert asuka.allSolFiles == [str(sol)]


def test_empty_root_collects_no_files():
    asuka = Asuka(_root="")
    assert asuka.allSolFiles == []
    assert asuka.file_count() == 0


def test_directory_without_sol_files_raises(tmp_path):
    (tmp_path / "readme.txt").write_text("no contracts here")
    with pytest.raises(ValueError, match="Solidity file not found"):
        Asuka(_root=str(tmp_path))


def test_detector_crash_is_isolated(monkeypatch):
    """A crashing detector surfaces as an error, never as a pool abort."""
    from vuls.reentrancy import Reentrancy

    def boom(self, scan):
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(Reentrancy, "check", boom)
    asuka = Asuka(_root=str(TEST_DATA / "reentrancy.sol"))
    vul_list, error = asuka._scan_file_isolated(
        (str(TEST_DATA / "reentrancy.sol"), [107])
    )
    assert vul_list is None
    assert "Detector failed" in error
    assert "reentrancy.sol" in error
