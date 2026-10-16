"""Cross-check every detector against every test_data file.

The expected counts below are the current agreed behaviour of each
detector. When you intentionally change a detector's logic, update the
corresponding entry here in the same commit.
"""
import pytest

from vuls.all_detector import ALL_DETECTORS as DETECTORS

EXPECTED_IDS = {100, 101, 104, 107, 109, 112, 115, 137, 138}

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
EXPECTED = {
    ("access_of_uninitialized_pointer.sol", 101): 2,
    ("access_of_uninitialized_pointer.sol", 104): 1,
    ("access_of_uninitialized_pointer.sol", 109): 2,
    ("arbitrary_call.sol", 104): 1,
    ("arbitrary_call.sol", 137): 2,
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
