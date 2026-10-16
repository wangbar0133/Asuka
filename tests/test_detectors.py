"""Cross-check every detector against every test_data file.

The expected counts below are the current agreed behaviour of each
detector. When you intentionally change a detector's logic, update the
corresponding entry here in the same commit.
"""
import pytest

from vuls.all_detector import ALL_DETECTORS as DETECTORS

EXPECTED_IDS = {100, 101, 104, 106, 107, 109, 112, 115, 116, 120, 137, 138,
                201, 202, 203, 204, 205, 206}

ALL_FILES = [
    "access_of_uninitialized_pointer.sol",
    "arbitrary_call.sol",
    "bec.sol",
    "delegatecall.sol",
    "function_default_visibility.sol",
    "msgvalue_in_loop.sol",
    "reentrancy.sol",
    "test.sol",
    "tx_origin.sol",
    "unchecked_return_value.sol",
]

# (file, SWC id) -> expected number of findings.
# Any combination not listed here must report exactly 0 findings.
# Batch-1 detector additions and the cast-expression scanner fix:
# access_of_uninitialized_pointer.sol gained s101 (the % and + inside
# uint8(sha3(...)) were previously invisible to the Scanner), s106
# (unprotected suicide), s116 (now in a condition), s120 (sha3 with
# chain attributes), s205 (suicide + sha3); arbitrary_call.sol gained
# s201 (IERC20(token).transferFrom result discarded).
EXPECTED = {
    ("access_of_uninitialized_pointer.sol", 101): 3,
    ("access_of_uninitialized_pointer.sol", 104): 1,
    ("access_of_uninitialized_pointer.sol", 106): 1,
    ("access_of_uninitialized_pointer.sol", 109): 2,
    ("access_of_uninitialized_pointer.sol", 116): 1,
    ("access_of_uninitialized_pointer.sol", 120): 1,
    ("access_of_uninitialized_pointer.sol", 205): 2,
    ("arbitrary_call.sol", 104): 1,
    ("arbitrary_call.sol", 137): 2,
    ("arbitrary_call.sol", 201): 1,
    ("bec.sol", 100): 2,
    ("bec.sol", 101): 2,
    ("delegatecall.sol", 112): 1,
    ("function_default_visibility.sol", 100): 2,
    ("function_default_visibility.sol", 104): 1,
    ("msgvalue_in_loop.sol", 138): 1,
    ("reentrancy.sol", 101): 2,
    ("reentrancy.sol", 107): 3,
    ("test.sol", 100): 2,
    ("test.sol", 101): 2,
    ("tx_origin.sol", 104): 1,
    ("tx_origin.sol", 115): 1,
    ("unchecked_return_value.sol", 104): 1,
}


def test_detector_registry():
    """All detectors are registered with consistent metadata."""
    assert set(DETECTORS) == EXPECTED_IDS
    for vul_id, detector in DETECTORS.items():
        assert detector.ID == vul_id
        assert detector.NAME
        assert detector.DESCRIPTION
        assert detector.ADVICE
        assert detector.RISK in (0, 1, 2, 3)


@pytest.mark.parametrize("file", ALL_FILES)
@pytest.mark.parametrize("vul_id", sorted(EXPECTED_IDS))
def test_detector_on_file(scan_file, file, vul_id):
    vuls = DETECTORS[vul_id].check(scan_file(file))
    expected = EXPECTED.get((file, vul_id), 0)
    assert len(vuls.vul_list) == expected, (
        f"s{vul_id} on {file}: expected {expected} findings, "
        f"got {len(vuls.vul_list)}"
    )


@pytest.mark.parametrize(
    "file,vul_id",
    sorted((file, vul_id) for (file, vul_id), count in EXPECTED.items() if count),
)
def test_findings_carry_location(scan_file, file, vul_id):
    """Every reported finding must reference the scanned file and a location."""
    vuls = DETECTORS[vul_id].check(scan_file(file))
    assert vuls.vul_list
    for vul in vuls.vul_list:
        assert file in vul.fileName
        assert vul.locList


# ---------------------------------------------------------------------------
# Branch-level tests on the targeted fixtures in tests/fixtures/.
# These pin down specific discrimination logic and false-positive
# resistance; they are intentionally outside the EXPECTED matrix.
# ---------------------------------------------------------------------------


class TestReentrancyBranches:
    def test_storage_pointer_write_after_call(self, scan_fixture):
        """SWC-107 must fire for storage-pointer member writes (s.v = x)."""
        vuls = DETECTORS[107].check(scan_fixture("storage_re.sol"))
        assert vuls.vul_count() == 2  # s.v write + state var total

    def test_view_function_with_call_is_skipped(self, scan_fixture):
        """view functions are skipped via stateMutability, not visibility."""
        scan = scan_fixture("storage_re.sol")
        get_view = next(
            f for f in scan.functions if f.functionObject.stateMutability == "view"
        )
        # the view function contains a call but must not produce findings
        assert any(c.name == "call" for c in get_view.functionCalls)


class TestUncheckedReturnBranches:
    def test_checked_and_unchecked_call_results(self, scan_fixture):
        """require(success) removes a call result from the report.

        guards() exercises every require() shape that must NOT clear
        the map: member-access calls, non-require calls, literal
        arguments and unknown names.
        """
        vuls = DETECTORS[104].check(scan_fixture("unchecked_return.sol"))
        # uncheckedVar's `sent` + mixed's bare call + guards' `ok`
        # (none of them required); checked()'s success IS required
        assert vuls.vul_count() == 3


class TestTxOriginRobustness:
    def test_zero_argument_require_does_not_crash(self, scan_fixture):
        """tx_origin assumed require() always has an argument.

        unchecked_return.sol's guards() contains a bare require();
        arguments[0] used to raise IndexError.
        """
        vuls = DETECTORS[115].check(scan_fixture("unchecked_return.sol"))
        assert vuls.vul_count() == 0
        assert vuls.id == 115


class TestArbitraryCallFalsePositives:
    def test_near_miss_patterns_report_nothing(self, scan_fixture):
        """All near-miss call shapes must be rejected.

        Covers: view functions, multi-arg constructors, non-identifier
        args, state-var / non-address args, non-identifier callees and
        call() with non-bytes or non-parameter arguments.
        """
        vuls = DETECTORS[137].check(scan_fixture("negative_calls.sol"))
        assert vuls.vul_count() == 0


class TestDelegatecallRobustness:
    def test_bare_delegatecall_does_not_crash(self, scan_fixture):
        """A bare delegatecall(data) statement has no callee expression.

        This used to crash the detector with AttributeError before the
        hasattr/None fix.
        """
        vuls = DETECTORS[112].check(scan_fixture("negative_calls.sol"))
        assert vuls.vul_count() == 0
        assert vuls.id == 112
        assert vuls.name == "Delegatecall to Untrusted Callee"


# ---------------------------------------------------------------------------
# Batch-1 detectors (SWC 106/116/120 + custom 201-206).
# ---------------------------------------------------------------------------


def _reported_lines(vuls) -> list[int]:
    return sorted(
        loc["start"]["line"]
        for vul in vuls.vul_list
        for loc in vul.locList
    )


class TestSuicidal:
    def test_only_unprotected_public_selfdestruct(self, scan_fixture):
        """bad() fires; the onlyOwner and internal paths do not."""
        vuls = DETECTORS[106].check(scan_fixture("suicidal.sol"))
        assert vuls.vul_count() == 1
        assert _reported_lines(vuls) == [11]


class TestWeakPRNG:
    def test_hash_of_chain_attributes(self, scan_fixture):
        """keccak256 over timestamp/blockhash/number fire; user seed does not."""
        vuls = DETECTORS[120].check(scan_fixture("randomness.sol"))
        assert vuls.vul_count() == 3
        assert _reported_lines(vuls) == [8, 12, 16]


class TestTimestampDependence:
    def test_only_conditions_and_requires(self, scan_fixture):
        """require/while conditions fire; a plain return does not."""
        vuls = DETECTORS[116].check(scan_fixture("randomness.sol"))
        assert vuls.vul_count() == 2
        assert _reported_lines(vuls) == [24, 35]


class TestDivideBeforeMultiply:
    def test_division_under_multiplication_only(self, scan_fixture):
        """a / b * c and a % b * c fire; a * c / b and a / b + c * a do not."""
        vuls = DETECTORS[202].check(scan_fixture("arithmetic.sol"))
        assert vuls.vul_count() == 2
        assert _reported_lines(vuls) == [10, 14]


class TestTautology:
    def test_self_comparison_only(self, scan_fixture):
        """x == x, a == a and this.flag == this.flag fire; x == y does not."""
        vuls = DETECTORS[203].check(scan_fixture("arithmetic.sol"))
        assert vuls.vul_count() == 3
        assert _reported_lines(vuls) == [26, 30, 34]


class TestIncorrectUnary:
    def test_comparison_with_unary_operand(self, scan_fixture):
        """!flag == true and ~z > 3 fire; a bare !true does not."""
        vuls = DETECTORS[206].check(scan_fixture("arithmetic.sol"))
        assert vuls.vul_count() == 2
        assert _reported_lines(vuls) == [42, 46]


class TestUncheckedTransfer:
    def test_only_token_transfers_without_checks(self, scan_fixture):
        """Token transfers with a discarded result fire.

        Reported: param / state var / cast / member chain
        (pool.token) and the contract's own transfer() body.
        Not reported: require(t.transfer(...)), this.transfer(...)
        (own function, line 44) and the ether-transfer shapes
        - payable(x), msg.sender, address(this), wallets[0].addr -
        which belong to the unchecked-return-value detector.
        (s104 also reports the token lines: that overlap is a documented
        limitation of its syntactic METHED matching.)
        """
        vuls = DETECTORS[201].check(scan_fixture("token_transfer.sol"))
        assert _reported_lines(vuls) == [24, 28, 32, 36, 48]
        assert 44 not in _reported_lines(vuls)   # this.transfer(...)
        assert 55 not in _reported_lines(vuls)   # wallets[0].addr.transfer

    def test_cast_transfer_also_flags_arbitrary_call(self, scan_fixture):
        """IERC20(t).transfer with a controllable address param is s137."""
        vuls = DETECTORS[137].check(scan_fixture("token_transfer.sol"))
        assert vuls.vul_count() == 1
        assert _reported_lines(vuls) == [31]


class TestDeprecatedStandards:
    def test_suicide_sha3_and_msg_gas(self, scan_fixture):
        vuls = DETECTORS[205].check(scan_fixture("deprecated.sol"))
        assert vuls.vul_count() == 2
        assert _reported_lines(vuls) == [5, 9]


class TestRTLO:
    def test_bidi_control_character_is_reported(self, tmp_path):
        sol = tmp_path / "rtlo.sol"
        sol.write_text(
            'pragma solidity ^0.8.0;\n'
            'contract C {\n'
            '    string public bad = "evil\u202echar";\n'
            '}\n',
            encoding="utf-8",
        )
        from tests.conftest import make_scanner

        vuls = DETECTORS[204].check(make_scanner(sol))
        assert vuls.vul_count() == 1
        assert _reported_lines(vuls) == [3]

    def test_clean_source_is_not_reported(self, scan_fixture):
        vuls = DETECTORS[204].check(scan_fixture("deprecated.sol"))
        assert vuls.vul_count() == 0

    def test_unreadable_file_is_ignored(self, scan_fixture):
        scan = scan_fixture("deprecated.sol")
        scan.fileName = "/nonexistent/unreadable.sol"
        assert DETECTORS[204].check(scan).vul_count() == 0


class TestDetectorBaseClass:
    def test_check_must_be_implemented(self):
        from vuls.detector import Detector

        with pytest.raises(NotImplementedError):
            Detector().check(None)

    def test_result_carries_metadata(self):
        from vuls.detector import Detector

        class Sample(Detector):
            NAME = "Sample"
            ID = 999
            DESCRIPTION = "d"
            ADVICE = "a"
            RISK = 2

        result = Sample().result([])
        assert (result.name, result.id, result.risk) == ("Sample", 999, 2)
        assert result.vul_count() == 0
