"""Cross-check every detector against every test_data file.

The expected counts below are the current agreed behaviour of each
detector. When you intentionally change a detector's logic, update the
corresponding entry here in the same commit.
"""
import pytest

from vuls import all_detector

DETECTORS = {
    module.ID: module
    for name in dir(all_detector)
    if hasattr(module := getattr(all_detector, name), "check")
}

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
    """All detectors are auto-discovered from vuls.all_detector."""
    assert set(DETECTORS) == EXPECTED_IDS
    for vul_id, module in DETECTORS.items():
        assert module.ID == vul_id
        assert module.NAME
        assert module.DESCREIBE
        assert module.ADVICE
        assert module.RISK in (0, 1, 2, 3)


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
