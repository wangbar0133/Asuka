"""CLI-layer tests: argument parsing helpers and an end-to-end subprocess run."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from core.__main__ import parse_vuls_string

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestParseVulsString:
    def test_mixed_ids(self):
        assert parse_vuls_string("s100,101,107,s115") == [100, 101, 107, 115]

    def test_single_id(self):
        assert parse_vuls_string("100") == [100]
        assert parse_vuls_string("s137") == [137]

    def test_duplicates_are_kept(self):
        assert parse_vuls_string("100,100") == [100, 100]

    def test_unknown_detector_exits(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            parse_vuls_string("100,asdf,999")
        assert exc_info.value.code == 1
        assert "Unkonw detectors" in capsys.readouterr().out


def _run_cli(*args, timeout=120):
    return subprocess.run(
        [sys.executable, "-m", "core", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=timeout,
    )


def test_cli_version():
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "0.2.1" in result.stdout


def test_cli_scan_single_file():
    result = _run_cli("test_data/reentrancy.sol")
    assert result.returncode == 0
    # reentrancy.sol: 2x int-overflow + 3x reentrancy
    assert "5 vuls were found" in result.stdout
    assert "Reentrancy" in result.stdout


def test_cli_scan_with_include_filter():
    result = _run_cli("test_data/reentrancy.sol", "-i", "s107")
    assert result.returncode == 0
    assert "3 vuls were found" in result.stdout
    assert "Int Overflow" not in result.stdout


def test_cli_reports_broken_files_without_aborting(tmp_path):
    (tmp_path / "broken.sol").write_text("this is not solidity {{{ !!!")
    shutil.copy(REPO_ROOT / "test_data" / "reentrancy.sol", tmp_path / "clean.sol")

    result = _run_cli(str(tmp_path))
    assert result.returncode == 0
    # clean.sol findings still reported: 2x s101 + 3x s107
    assert "5 vuls were found" in result.stdout
    assert "1 file(s) failed to scan" in result.stdout
    assert "broken.sol" in result.stdout
