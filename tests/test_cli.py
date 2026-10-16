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


def test_cli_list_detectors():
    result = _run_cli("-d")
    assert result.returncode == 0
    assert "Find 9 detectors" in result.stdout
    for vul_id in (100, 101, 104, 107, 109, 112, 115, 137, 138):
        assert "s{}".format(vul_id) in result.stdout


def test_cli_exclude_detector():
    result = _run_cli("test_data/reentrancy.sol", "-e", "s107")
    assert result.returncode == 0
    # only int-overflow remains: 2 findings
    assert "2 vuls were found" in result.stdout
    assert "Reentrancy" not in result.stdout


def test_cli_thread_count():
    result = _run_cli("test_data/reentrancy.sol", "-t", "2")
    assert result.returncode == 0
    assert "5 vuls were found" in result.stdout


def test_cli_unknown_detector_exits():
    result = _run_cli("test_data/reentrancy.sol", "-i", "999")
    assert result.returncode == 1
    assert "Unkonw detectors" in result.stdout


def test_cli_address_without_apikey_exits():
    result = _run_cli("0x" + "ab" * 20)
    assert result.returncode == 1
    assert "No API Keys!" in result.stdout


def test_cli_address_without_chain_exits():
    result = _run_cli("0x" + "ab" * 20, "-k", "some-key")
    assert result.returncode == 1
    assert "No Chain Type!" in result.stdout


class TestMainInProcess:
    """Drive main() directly so coverage sees the CLI wiring."""

    def test_main_scan(self, monkeypatch, capsys):
        from core import __main__ as core_main

        monkeypatch.setattr(
            sys, "argv", ["asuka", "test_data/reentrancy.sol"]
        )
        core_main.main()
        out = capsys.readouterr().out
        assert "5 vuls were found" in out
        assert "s107:Reentrancy" in out

    def test_main_broken_file_reported(self, monkeypatch, capsys, tmp_path):
        from core import __main__ as core_main

        (tmp_path / "broken.sol").write_text("garbage {{{")
        monkeypatch.setattr(sys, "argv", ["asuka", str(tmp_path)])
        core_main.main()
        out = capsys.readouterr().out
        assert "failed to scan" in out

    def test_list_detectors_action(self, capsys):
        from core import __main__ as core_main

        with pytest.raises(SystemExit) as exc_info:
            core_main.parser.parse_args(["-d"])
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Find 9 detectors" in out

    def test_main_include_filter(self, monkeypatch, capsys):
        from core import __main__ as core_main

        monkeypatch.setattr(
            sys, "argv",
            ["asuka", "test_data/reentrancy.sol", "-i", "s107"],
        )
        core_main.main()
        out = capsys.readouterr().out
        assert "3 vuls were found" in out

    def test_main_exclude_and_thread(self, monkeypatch, capsys):
        from core import __main__ as core_main

        monkeypatch.setattr(
            sys, "argv",
            ["asuka", "test_data/reentrancy.sol", "-e", "s107", "-t", "2"],
        )
        core_main.main()
        out = capsys.readouterr().out
        assert "2 vuls were found" in out

    def test_main_address_without_key_exits(self, monkeypatch, capsys):
        from core import __main__ as core_main

        monkeypatch.setattr(sys, "argv", ["asuka", "0x" + "ab" * 20])
        with pytest.raises(SystemExit) as exc_info:
            core_main.main()
        assert exc_info.value.code == 1
        assert "No API Keys!" in capsys.readouterr().out

    def test_main_address_without_chain_exits(self, monkeypatch, capsys):
        from core import __main__ as core_main

        monkeypatch.setattr(
            sys, "argv", ["asuka", "0x" + "ab" * 20, "-k", "key"]
        )
        with pytest.raises(SystemExit) as exc_info:
            core_main.main()
        assert exc_info.value.code == 1
        assert "No Chain Type!" in capsys.readouterr().out

    def test_main_address_flow(self, monkeypatch, capsys, tmp_path):
        """Full address flow: key + chain, scraper stubbed out."""
        import core.asuka as asuka_module
        from core import __main__ as core_main

        sol = tmp_path / "Token.sol"
        sol.write_text("contract Token {}")

        class StubScraper:
            def __init__(self, chainType, apiKey):
                pass

            def get_source_code(self, address):
                return str(tmp_path)

        monkeypatch.setattr(asuka_module, "Scraper", StubScraper)
        monkeypatch.setattr(
            sys, "argv",
            ["asuka", "0x" + "ab" * 20, "-k", "key", "-c", "eth"],
        )
        core_main.main()
        out = capsys.readouterr().out
        assert "1 solidity contract files were found" in out
        assert "0 vuls were found" in out
