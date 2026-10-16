"""Keep README.md and CHANGELOG.md in sync with the code.

These tests fail when the detector registry, the CLI options or the
package version change without the documentation being updated - the
documentation drift that used to go unnoticed.
"""
import re
from pathlib import Path

from core import __version__
from core.__main__ import parser
from vuls.all_detector import ALL_DETECTORS, DETECTOR_IDS

README = Path(__file__).resolve().parent.parent / "README.md"
CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
TEXT = README.read_text(encoding="utf-8")
CHANGELOG_TEXT = CHANGELOG.read_text(encoding="utf-8")

OPTION_RE = re.compile(r"--?[a-zA-Z][a-zA-Z-]*")


def _readme_usage_line() -> str:
    return next(
        line for line in TEXT.splitlines() if line.startswith("usage: asuka")
    )


def test_detector_table_lists_exactly_the_registered_ids():
    documented = {
        int(match.group(1))
        for match in re.finditer(r"^\|\s*(?:SWC-)?(\d+)\s*\|", TEXT, re.M)
    }
    assert documented == set(DETECTOR_IDS)


def test_detector_names_are_documented():
    missing = [
        detector.NAME for detector in ALL_DETECTORS.values()
        if detector.NAME not in TEXT
    ]
    assert not missing, f"detector names missing from README: {missing}"


def test_usage_line_documents_the_real_cli_options():
    documented = set(OPTION_RE.findall(_readme_usage_line()))
    actual = set(OPTION_RE.findall(parser.format_usage()))
    assert documented == actual, (
        f"README usage options {sorted(documented)} != CLI {sorted(actual)}"
    )


def test_install_and_development_snippets_use_the_dev_extra():
    """The documented setup commands must keep working as written."""
    assert '.venv/bin/pip install -e ".[dev]"' in TEXT
    assert "python3.11 -m venv .venv" in TEXT


def test_cross_file_section_is_present():
    assert "## Cross-file scanning" in TEXT
    assert "resolution-only" in TEXT


def test_changelog_top_entry_matches_the_package_version():
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\] - (.+)$", CHANGELOG_TEXT, re.M)
    assert match, "CHANGELOG.md has no '## [x.y.z] - date' heading"
    assert match.group(1) == __version__, (
        f"CHANGELOG top entry {match.group(1)} != package version {__version__}"
    )
    assert match.group(2).strip() != "unreleased", (
        "the CHANGELOG top entry still says 'unreleased'"
    )


def test_changelog_documents_every_detector_id():
    documented = set(re.findall(r"`(?:SWC-)?(\d+)`", CHANGELOG_TEXT))
    missing = {str(vul_id) for vul_id in DETECTOR_IDS} - documented
    assert not missing, f"detector ids missing from CHANGELOG: {sorted(missing)}"


def test_readme_links_the_changelog():
    assert "[CHANGELOG.md](CHANGELOG.md)" in TEXT
