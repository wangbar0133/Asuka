import argparse
import logging

from vuls.all_detector import ALL_DETECTORS, DETECTOR_IDS

from . import __version__
from .asuka import Asuka
from .printer import Printer
from .utils import check_address


class ListAllDetectors(argparse.Action):

    def __call__(self, parser: argparse.ArgumentParser, *args, **kwargs) -> None:
        Printer.print_blue(f"Find {len(DETECTOR_IDS)} detectors:")
        Printer.print_detectors(DETECTOR_IDS, ALL_DETECTORS)
        parser.exit()


parser = argparse.ArgumentParser()

parser.add_argument("path", help="Folders or solidity files or address.")
parser.add_argument("--version",version=__version__, action="version", help="Show current version")
parser.add_argument("-k", "--apikey", help="Api key")
parser.add_argument("-c", "--chain", help="chain type")

groupCheckList = parser.add_argument_group("Check List")
groupDetect = parser.add_argument_group("Detect")

groupCheckList.add_argument(
    "-d", "--detector",
    action=ListAllDetectors,
    nargs=0,
    help="Show all detectors",
    default=False
)
groupDetect.add_argument("-i", "--include", help="Specify the detector")
groupDetect.add_argument("-e", "--exclude", help="Exclusion detector")
groupDetect.add_argument("-t", "--thread", help="Number of threads")

def parse_vuls_string(s: str) -> list[int]:
    """
        This function can parse the input vuls string.
        Like 100 & s100 & 101,102 & s101,102,s103.
        Return a int list of all vuls.
    """
    vuls: list[int] = []
    unValidVuls: list[str] = []
    for item in s.split(","):
        if item[0] == "s":
            item = item[1:]
        if item.isdigit():
            if int(item) in DETECTOR_IDS:
                vuls.append(int(item))
                continue
        unValidVuls.append(item)
    if unValidVuls:
        for unValidVul in unValidVuls:
            Printer.print_red("Unknown detectors:")
            print(unValidVul)
            exit(1)
    return vuls

def main() -> None:
    logging.basicConfig(
        filename="debug.log",
        filemode="w",
        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG
    )
    args = parser.parse_args()
    Printer.print_banner()

    if args.path:
        root = args.path
        if args.include:
            detectors = sorted(parse_vuls_string(args.include))
        elif args.exclude:
            detectors = sorted(list(set(DETECTOR_IDS) - set(parse_vuls_string(args.exclude))))
        else:
            detectors = DETECTOR_IDS

        if args.thread:
            thread = int(args.thread)
        else:
            thread = 4

        if check_address(root):
            if not args.apikey:
                Printer.print_red("No API Keys!")
                exit(1)
            if not args.chain:
                Printer.print_red("No Chain Type!")
                exit(1)
            apiKey = args.apikey
            chainType = args.chain.upper()
        else:
            apiKey = None
            chainType = None

        # Create a Asuka object
        asuka = Asuka(_root=root, _detectors=detectors, _threads=thread, _chainType=chainType,_apiKey=apiKey)
        Printer.print_files(asuka.allSolFiles)
        Printer.print_blue("Check list:")
        Printer.print_detectors(detectors, ALL_DETECTORS)
        # Printer.print_yellow("Antlr4 warn:")

        # Start scan task
        asuka.scan()
        Printer.print_green("\n\n--------------------------Finish--------------------------\n")
        if asuka.errors:
            Printer.print_red(f"{len(asuka.errors)} file(s) failed to scan:")
            for error in asuka.errors:
                print(f"  {error}")
            print("\n")
        Printer.print_summary(asuka.vulTable)
        Printer.print_vul_table(asuka.vulTable)


if __name__ == "__main__":
    main()
