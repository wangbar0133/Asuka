"""Finding data model: Vul (single finding), Vuls (per-detector results),
VulTable (per-scan aggregation keyed by SWC id)."""


class Vuls:

    def __init__(self, name: str, id: int, description: str, advice: str,
                 risk: int, vulList: list):
        self.name = name
        self.id = id
        self.description = description
        self.advice = advice
        self.vul_list = vulList
        self.risk = risk

    def vul_count(self) -> int:
        return len(self.vul_list)

    def __add__(self, _vuls: "Vuls") -> "Vuls":
        "merge all same type vul from different files"
        if not hasattr(_vuls, "id"):
            raise ValueError("There is no name attr!")
        if self.id == _vuls.id:
            self.vul_list += _vuls.vul_list
        else:
            raise ValueError("Wrong vul type!")
        return self


class Vul:

    def __init__(self, fileName: str, locList: list[dict]):
        self.fileName = fileName
        self.locList = locList


class VulTable(dict):

    def __init__(self, _detectors: list[int]):
        for detector in _detectors:
            self[detector] = None

    def __add__(self, _vuls: Vuls) -> "VulTable":
        if not self[_vuls.id]:
            self[_vuls.id] = _vuls
        else:
            self[_vuls.id] += _vuls
        return self

    def count_table(self) -> dict[int, int]:
        countTable = {3: 0, 2: 0, 1: 0, 0: 0}
        for vuls in self.values():
            # entries stay None when no file ever ran that detector
            # (e.g. every file in the scan failed to parse)
            if vuls is None:
                continue
            countTable[vuls.risk] += vuls.vul_count()
        return countTable

    def vul_count(self) -> int:
        count = 0
        for vuls in self.values():
            if vuls is None:
                continue
            count += vuls.vul_count()
        return count

    def sort_by_risk(self) -> list[Vuls]:
        vulList = sorted(
            [
                vul for vul in self.values()
                if vul is not None
            ],
            key=lambda x: x.risk,
            reverse=True
        )
        return vulList


class Color:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    END = "\033[0m"


Risk: dict[int, str] = {
    0: "Info",
    1: Color.BLUE + "Low" + Color.END,
    2: Color.YELLOW + "Medium" + Color.END,
    3: Color.RED + "High" + Color.END,
}
