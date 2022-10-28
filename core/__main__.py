import argparse

from .printer import Printer
from .asuka import Asuka
from vuls import all_detector

class ListAllDetectors(argparse.Action):
    
    def __call__(self, parser, *args, **kwargs):
        Printer.print_blue("Find {} detectors:".format(len(allDetectorList)))
        Printer.print_detectors(allDetectorList, allDetectorTable)
        parser.exit()

# load all detector
allDetectorTable = dict()
allDetectorList = list()
for attrName in dir(all_detector):
    if hasattr(getattr(all_detector, attrName), "check"):
        detetor = getattr(all_detector, attrName)
        allDetectorTable[detetor.ID] = detetor
        allDetectorList.append(detetor.ID)
allDetectorList.sort()


parser = argparse.ArgumentParser()

parser.add_argument("path", help="Folders or solidity files.")
parser.add_argument("--version",version="0.1.0", action="version", help="Show current version")

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
        
def parse_vuls_string(s) -> list:
    vuls = list()
    unValidVuls = list()
    for item in s.split(","):
        if item[0] == "s":
            item = item[1:]
        if item.isdigit():
            if int(item) in allDetectorList:
                vuls.append(int(item))
                continue
        unValidVuls.append(item)
    if unValidVuls:
        for unValidVul in unValidVuls:
            Printer.print_red("Unkonw detectors:")
            print(unValidVul)
            exit(1)
    return vuls

def main():
    args = parser.parse_args()
    Printer.print_banner()
        
    if args.path:
        root = args.path
        if args.include:
            detectors = sorted(parse_vuls_string(args.include))
        elif args.exclude:
            detectors = sorted(list(set(allDetectorList) - set(parse_vuls_string(args.exclude))))
        else:
            detectors = allDetectorList
        
        if args.thread:
            thread = int(args.thread)
        else:
            thread = 4
        
        asuka = Asuka(_root=root, _detectors=detectors, _threads=thread)
        Printer.print_files(asuka.allSolFiles)
        Printer.print_blue("Check list:")
        Printer.print_detectors(detectors, allDetectorTable)
        Printer.print_yellow("Antlr4 warn:")
        
        asuka.scan()
        Printer.print_green("\n\n--------------------------Finsh--------------------------\n")
        Printer.print_summary(asuka.vulTable)
        Printer.print_vul_table(asuka.vulTable)