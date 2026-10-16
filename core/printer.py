import prettytable

from vuls.detector import Detector
from vuls.vul import Risk, Vuls, VulTable

from . import __version__
from .utils import merge_loc_list

BANNER = r"""

 ______                   __
/\  _  \                 /\ \
\ \ \L\ \    ____  __  __\ \ \/'\      __
 \ \  __ \  /',__\/\ \/\ \\ \ , <    /'__`\
  \ \ \/\ \/\__, `\ \ \_\ \\ \ \\`\ /\ \L\.\_
   \ \_\ \_\/\____/\ \____/ \ \_\ \_\ \__/.\_\
    \/_/\/_/\/___/  \/___/   \/_/\/_/\/__/\/_/

    version {version}

    Extremely Fast Contract Defect Detectors
    https://github.com/wangbar0133/Asuka


"""


class Printer:
    """
        A class to print info on cli.
    """

    @staticmethod
    def print_banner() -> None:
        print(Color.RED + BANNER.format(version=__version__) + Color.END)

    @staticmethod
    def print_detectors(allDetectorList: list[int],
                        allDetectorTable: dict[int, Detector]) -> None:
        detectorTable = prettytable.PrettyTable()
        detectorTable.field_names = ["ID", "NAME", "RISK"]
        for vulId in allDetectorList:
            detectorTable.add_row(
                [
                    f"s{vulId.__str__()}",
                    allDetectorTable[vulId].NAME,
                    Risk[allDetectorTable[vulId].RISK]
                ]
            )
        print(detectorTable)
        print("\n")

    @staticmethod
    def print_files(paths: list[str]) -> None:
        Printer.print_blue(f"{len(paths).__str__()} solidity contract files were found")
        for path in paths:
            Printer.print_green(path)
        print("\n")

    @staticmethod
    def print_summary(vulTable: VulTable) -> None:
        countTable = vulTable.count_table()
        count = vulTable.vul_count()
        Printer.print_blue(f"{count.__str__()} vuls were found")
        for i in [3, 2, 1, 0]:
            Printer.print_risk_color("{} {}".format("-"*countTable[i], countTable[i].__str__()), i)
        print("\n")
        showVulTable = prettytable.PrettyTable()
        Printer.print_blue("Summary:")
        showVulTable.field_names = ["ID", "NAME", "RISK", "NUM"]
        for vulId in vulTable.keys():
            if vulTable[vulId] is None:
                continue
            showVulTable.add_row(
                [
                    f"s{vulId.__str__()}",
                    vulTable[vulId].name,
                    Risk[vulTable[vulId].risk],
                    vulTable[vulId].vul_count()
                ]
            )
        print(showVulTable)
        print("\n")

    @staticmethod
    def print_vul_table(vulTable: VulTable) -> None:
        vulList = vulTable.sort_by_risk()
        for vul in vulList:
            if len(vul.vul_list) == 0:
                continue
            Printer.print_risk_color(
                text="s" + str(vul.id) + ":" + vul.name,
                risk=vul.risk
            )
            print(f"Description: {vul.description}")
            print(f"Advice: {vul.advice}")
            print(f"Detail: https://swcregistry.io/docs/SWC-{str(vul.id)}\n")
            Printer._code_snippet(vul)
            print("\n")

    @staticmethod
    def _code_snippet(vuls: Vuls) -> None:
        for vul in vuls.vul_list:
            Printer.print_blue(f"\n{vul.fileName}\n")
            for loc in merge_loc_list(vul.locList):
                with open(vul.fileName, encoding="utf-8") as f:
                    codeLines = [line.split("\n")[0] for line in f.readlines()]
                start = loc["start"]["line"]
                end = loc["end"]["line"]
                if start == 1:
                    top = 0
                else:
                    top = start - 2
                if end > len(codeLines):
                    bottom = len(codeLines)
                else:
                    bottom = end
                for lineIndex, codeLine in enumerate(codeLines[top:bottom+1]):
                    line = top + lineIndex
                    if line == top or line == bottom:
                        print(f"{str(line+1)}|".rjust(7) + codeLine)
                    else:
                        Printer.print_yellow(f">{str(line+1)}|".rjust(7) + codeLine)
                print("\n")

    @staticmethod
    def print_file_num(num: int) -> None:
        print("Contract files: " + Color.GREEN + str(num) + Color.END)

    @staticmethod
    def print_risk_color(text: str, risk: int) -> None:
        if risk == 0:
            print(text)
        elif risk == 1:
            Printer.print_green(text)
        elif risk == 2:
            Printer.print_yellow(text)
        elif risk == 3:
            Printer.print_red(text)

    @staticmethod
    def print_green(text) -> None:
        print(Color.GREEN + str(text) + Color.END)

    @staticmethod
    def print_red(text) -> None:
        print(Color.RED + str(text) + Color.END)

    @staticmethod
    def print_blue(text) -> None:
        print(Color.BLUE + str(text) + Color.END)

    @staticmethod
    def print_yellow(text) -> None:
        print(Color.YELLOW + str(text) + Color.END)


class Color:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    END = "\033[0m"
