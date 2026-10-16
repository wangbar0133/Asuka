"""Unit tests for pure helper functions."""
import pytest

from core.utils import check_address, merge_loc_list
from vuls.utils import check_solc_version


class TestCheckAddress:
    @pytest.mark.parametrize(
        "address",
        [
            "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "0XDAC17F958D2EE523A2206206994597C13D831EC7",
            "0x0000000000000000000000000000000000000000",
        ],
    )
    def test_valid(self, address):
        assert check_address(address)

    @pytest.mark.parametrize(
        "address",
        [
            "",
            "dac17f958d2ee523a2206206994597c13d831ec7",  # no 0x prefix
            "0xdac17f958d2ee523a2206206994597c13d831ec",  # 39 hex chars
            "0xdac17f958d2ee523a2206206994597c13d831ecz",  # non-hex char
            "0x123",  # too short
        ],
    )
    def test_invalid(self, address):
        assert not check_address(address)


class TestCheckSolcVersion:
    @pytest.mark.parametrize(
        "pragma",
        ["<=0.8.0", "<0.8.0", "<0.7.0", "^0.7.0", "0.4.0", "0.7.6"],
    )
    def test_below_solc_8(self, pragma):
        assert check_solc_version(pragma, 8)

    @pytest.mark.parametrize("pragma", ["^0.8.0", "0.8.0", ">=0.8.0", "0.9.0"])
    def test_solc_8_or_newer(self, pragma):
        assert not check_solc_version(pragma, 8)

    def test_garbage_input_is_safe(self):
        assert not check_solc_version("", 8)
        assert not check_solc_version("solidity", 8)


def _loc(start, end):
    return {"start": {"line": start, "column": 0}, "end": {"line": end, "column": 9}}


class TestMergeLocList:
    def test_nearby_lines_are_merged(self):
        merged = merge_loc_list([_loc(10, 10), _loc(12, 12)])
        assert len(merged) == 1
        assert merged[0]["start"]["line"] == 10
        assert merged[0]["end"]["line"] == 12

    def test_distant_lines_are_kept_apart(self):
        merged = merge_loc_list([_loc(10, 10), _loc(50, 50)])
        assert len(merged) == 2

    def test_chain_of_nearby_lines(self):
        # gap is measured against the START line of the last merged entry
        merged = merge_loc_list([_loc(1, 1), _loc(3, 3), _loc(6, 6), _loc(30, 30)])
        assert [(m["start"]["line"], m["end"]["line"]) for m in merged] == [
            (1, 3),
            (6, 6),
            (30, 30),
        ]
