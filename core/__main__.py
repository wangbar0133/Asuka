import argparse

from .printer import Printer
from .asuka import Asuka
from vuls import all_detector

parser = argparse.ArgumentParser()
groupCheckList = parser.add_argument_group("Check List")
groupDetect = parser.add_argument_group("Detect")

groupDetect.add_argument("path", action="store", help="Folders or solidity files.")
groupCheckList.add_argument("-d", "--detector", action="store_true", help="Show all detectors.")
groupDetect.add_argument("-i", "--include", help="Specify the detector")
groupDetect.add_argument("-e", "--exclude", help="Exclusion detector")
groupDetect.add_argument("-t", "--thread", help="Number of threads.")

# load all detector
allDetectorTable = dict()
allDetectorList = list()
for attrName in dir(all_detector):
    if hasattr(getattr(all_detector, attrName), "check"):
        detetor = getattr(all_detector, attrName)
        allDetectorTable[detetor.ID] = detetor
        allDetectorList.append(detetor.ID)
allDetectorList.sort()

def parse_vuls_string(s) -> list():
    vuls = list()
    unValidVuls = list()
    for item in s.split(","):
        if item[0] == "s":
            item = item[1:]
        if item.isdigit():
            if int(item) in allDetectorList:
                vuls.append(item)
                continue
        unValidVuls.append(item)
    if unValidVuls:
        for unValidVul in unValidVuls:
            Printer.print_red("Unkonw detectors:")
            print(unValidVul)
            exit(1)
    return vuls

def main():
    Printer.print_banner()
    args = parser.parse_args()
    
    if args.detector:
        Printer.print_blue("Find {} detectors:".format(len(allDetectorList)))
        Printer.print_detectors(allDetectorList, allDetectorTable)
        exit(0) 
    
    if args.path:
        root = args.path
        if args.include:
            detectors = parse_vuls_string(arg.include).sort()
        elif args.exclude:
            detectors = [item for item in arg.exclude if item not in allDetectorList].sort()
        else:
            detectors = allDetectorList
        
        if args.thread:
            thread = arg.thread
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