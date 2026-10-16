"""Output-layer tests for core/printer.py (capsy-based)."""
import pytest

from core.printer import BANNER, Color, Printer
from vuls.reentrancy import check as reentrancy_check
from vuls.vul import Vul, Vuls, VulTable


@pytest.fixture(scope="module")
def reentrancy_table(scan_file):
    """A VulTable holding the 3 reentrancy findings of reentrancy.sol."""
    vuls = reentrancy_check(scan_file("reentrancy.sol"))
    table = VulTable([107])
    table += vuls
    return table


class TestBanner:
    def test_banner_contains_version_and_url(self, capsys):
        Printer.print_banner()
        out = capsys.readouterr().out
        assert "0.2.1" in out
        assert "github.com/wangbar0133/Asuka" in out
        assert Color.RED in out

    def test_banner_template_uses_version_placeholder(self):
        assert "{version}" in BANNER


class TestPrintDetectors:
    def test_lists_id_name_and_risk(self, capsys):
        from vuls import all_detector

        Printer.print_detectors([101], {101: all_detector.int_overflow})
        out = capsys.readouterr().out
        assert "s101" in out
        assert "Int Overflow" in out
        assert "High" in out


class TestPrintFiles:
    def test_counts_and_lists_paths(self, capsys):
        Printer.print_files(["a.sol", "b.sol"])
        out = capsys.readouterr().out
        assert "2 solidity contract files were found" in out
        assert "a.sol" in out
        assert "b.sol" in out


class TestPrintSummary:
    def test_summary_counts_and_table(self, capsys, reentrancy_table):
        Printer.print_summary(reentrancy_table)
        out = capsys.readouterr().out
        assert "3 vuls were found" in out
        # risk histogram bars for 3 high-severity findings
        assert "--- 3" in out
        assert "s107" in out
        assert "Reentrancy" in out


class TestPrintVulTable:
    def test_details_and_code_snippet(self, capsys, reentrancy_table):
        Printer.print_vul_table(reentrancy_table)
        out = capsys.readouterr().out
        assert "s107:Reentrancy" in out
        assert "Descreibe:" in out
        assert "Advice:" in out
        assert "Detail: https://swcregistry.io/docs/SWC-107" in out
        # code snippet with highlighted lines and the source file name
        assert "test_data/reentrancy.sol" in out
        assert ">" in out

    def test_empty_vul_list_prints_nothing(self, capsys):
        empty = Vuls(
            name="Empty", id=999, descreibe="d", advice="a", risk=1, vulList=[]
        )
        table = VulTable([999])
        table += empty
        Printer.print_vul_table(table)
        assert capsys.readouterr().out == ""


class TestRiskColors:
    @pytest.mark.parametrize("risk,color", [
        (0, None),
        (1, Color.GREEN),
        (2, Color.YELLOW),
        (3, Color.RED),
    ])
    def test_print_risk_color(self, capsys, risk, color):
        Printer.print_risk_color("TEXT", risk)
        out = capsys.readouterr().out
        if color is None:
            assert out == "TEXT\n"
        else:
            assert color in out

    @pytest.mark.parametrize("method,color", [
        ("print_green", Color.GREEN),
        ("print_red", Color.RED),
        ("print_blue", Color.BLUE),
        ("print_yellow", Color.YELLOW),
    ])
    def test_color_helpers(self, capsys, method, color):
        getattr(Printer, method)("X")
        assert color in capsys.readouterr().out


class TestSnippetEdgeCases:
    def test_snippet_clamps_end_line_past_eof(self, capsys):
        vul = Vul(
            fileName="test_data/tx_origin.sol",
            locList=[{
                "start": {"line": 1, "column": 0},
                "end": {"line": 10_000, "column": 0},
            }],
        )
        vuls = Vuls(
            name="Edge", id=999, descreibe="d", advice="a", risk=1, vulList=[vul]
        )
        Printer._code_snippet(vuls)
        out = capsys.readouterr().out
        # bottom is clamped to the file length (17 lines)
        assert "17|" in out

    def test_snippet_prints_header_per_file(self, capsys):
        """Findings from multiple files each print their own header."""
        vuls = Vuls(
            name="Multi", id=999, descreibe="d", advice="a", risk=2,
            vulList=[
                Vul(
                    fileName="test_data/reentrancy.sol",
                    locList=[{
                        "start": {"line": 12, "column": 0},
                        "end": {"line": 12, "column": 9},
                    }],
                ),
                Vul(
                    fileName="test_data/tx_origin.sol",
                    locList=[{
                        "start": {"line": 12, "column": 0},
                        "end": {"line": 12, "column": 9},
                    }],
                ),
            ],
        )
        Printer._code_snippet(vuls)
        out = capsys.readouterr().out
        assert "test_data/reentrancy.sol" in out
        assert "test_data/tx_origin.sol" in out


def test_print_file_num(capsys):
    Printer.print_file_num(3)
    out = capsys.readouterr().out
    assert "Contract files:" in out
    assert Color.GREEN + "3" in out
