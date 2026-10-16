"""Unit tests for the Vuls / Vul / VulTable data model."""
import pytest

from vuls.vul import Color, Risk, Vul, Vuls, VulTable


def make_vuls(vul_id=107, count=2, risk=3):
    return Vuls(
        name="SomeVul",
        id=vul_id,
        descreibe="describe",
        advice="advice",
        risk=risk,
        vulList=[
            Vul(
                fileName="f.sol",
                locList=[{"start": {"line": 1}, "end": {"line": 2}}],
            )
            for _ in range(count)
        ],
    )


class TestVuls:
    def test_attributes(self):
        vuls = make_vuls(count=3)
        assert vuls.name == "SomeVul"
        assert vuls.id == 107
        assert vuls.risk == 3
        assert vuls.vul_count() == 3

    def test_add_same_id_merges_findings(self):
        a = make_vuls(count=1)
        b = make_vuls(count=2)
        merged = a + b
        assert merged.vul_count() == 3

    def test_add_non_vuls_raises(self):
        with pytest.raises(ValueError, match="no name attr"):
            make_vuls() + "not a vuls"

    def test_add_different_id_raises(self):
        with pytest.raises(ValueError, match="Wrong vul type"):
            make_vuls(vul_id=107) + make_vuls(vul_id=101)


class TestVul:
    def test_carries_file_and_locations(self):
        vul = Vul(fileName="a.sol", locList=[{"start": {"line": 3}}])
        assert vul.fileName == "a.sol"
        assert vul.locList == [{"start": {"line": 3}}]


class TestVulTable:
    def test_add_stores_then_merges(self):
        table = VulTable([107])
        assert table[107] is None
        table += make_vuls(count=1)
        table += make_vuls(count=2)
        assert table[107].vul_count() == 3

    def test_count_table_groups_by_risk(self):
        table = VulTable([107, 101])
        table += make_vuls(vul_id=107, count=2, risk=3)
        table += make_vuls(vul_id=101, count=1, risk=2)
        assert table.count_table() == {3: 2, 2: 1, 1: 0, 0: 0}

    def test_vul_count_sums_all(self):
        table = VulTable([107, 101])
        table += make_vuls(vul_id=107, count=2)
        table += make_vuls(vul_id=101, count=1)
        assert table.vul_count() == 3

    def test_sort_by_risk_descends(self):
        table = VulTable([107, 101, 100])
        table += make_vuls(vul_id=107, count=1, risk=3)
        table += make_vuls(vul_id=101, count=1, risk=2)
        table += make_vuls(vul_id=100, count=1, risk=1)
        assert [v.id for v in table.sort_by_risk()] == [107, 101, 100]


class TestVulTableWithNoneEntries:
    """Entries stay None when no file ever produced results for a detector
    (e.g. every scanned file failed to parse)."""

    def test_none_entries_are_tolerated(self):
        table = VulTable([107, 101])
        table += make_vuls(vul_id=107, count=2)
        # 101 stays None
        assert table.count_table() == {3: 2, 2: 0, 1: 0, 0: 0}
        assert table.vul_count() == 2
        assert [v.id for v in table.sort_by_risk()] == [107]

    def test_all_none_table_is_empty(self):
        table = VulTable([107, 101])
        assert table.count_table() == {3: 0, 2: 0, 1: 0, 0: 0}
        assert table.vul_count() == 0
        assert table.sort_by_risk() == []


class TestRiskLevels:
    def test_risk_labels(self):
        assert Risk[0] == "Info"
        assert "Low" in Risk[1]
        assert "Medium" in Risk[2]
        assert "High" in Risk[3]
        assert Color.END in Risk[3]
