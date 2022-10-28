BANNER = r"""

 ______                   __                  
/\  _  \                 /\ \                 
\ \ \L\ \    ____  __  __\ \ \/'\      __     
 \ \  __ \  /',__\/\ \/\ \\ \ , <    /'__`\   
  \ \ \/\ \/\__, `\ \ \_\ \\ \ \\`\ /\ \L\.\_ 
   \ \_\ \_\/\____/\ \____/ \ \_\ \_\ \__/.\_\
    \/_/\/_/\/___/  \/___/   \/_/\/_/\/__/\/_/
                                              
    version 0.1.0                                           
                            
    Extremely Fast Contract Defect Detectors
    https://github.com/wangbar0133/Asuka
                                       

"""
import prettytable

from vuls.vul import Risk, VulTable, Vul, Vuls 

class Printer(object):
    
    @staticmethod
    def print_banner():
        print(Color.RED + BANNER + Color.END)
        
    @staticmethod
    def print_detectors(allDetectorList:list, allDetectorTable:VulTable):
        detectorTable = prettytable.PrettyTable()
        detectorTable.field_names = ["ID", "NAME", "RISK"]
        for vulId in allDetectorList:
            detectorTable.add_row(
                [
                    "s{}".format(vulId.__str__()), 
                    allDetectorTable[vulId].NAME, 
                    Risk[allDetectorTable[vulId].RISK]
                ]
            )
        print(detectorTable)
        print("\n")
    
    @staticmethod
    def print_files(paths:list):
        Printer.print_blue("{} solidity contract files were found".format(len(paths).__str__()))
        for path in paths:
            Printer.print_green(path) 
        print("\n")   
    
    @staticmethod
    def print_summary(vulTable:VulTable):
        countTable = vulTable.count_table()
        count = vulTable.vul_count()
        Printer.print_blue("{} vuls were found".format(count.__str__()))
        for i in [3, 2, 1, 0]:
            Printer.print_risk_color("{} {}".format("-"*countTable[i], countTable[i].__str__()), i)
        print("\n")
        showVulTable = prettytable.PrettyTable()
        Printer.print_blue("Summary:")
        showVulTable.field_names = ["ID", "NAME", "RISK", "NUM"]
        for vulId in vulTable.keys():
            showVulTable.add_row(
                [
                    "s{}".format(vulId.__str__()), 
                    vulTable[vulId].name, 
                    Risk[vulTable[vulId].risk],
                    vulTable[vulId].vul_count()
                ]
            )
        print(showVulTable)
        print("\n")
        
    @staticmethod
    def print_vul_table(vulTable: VulTable):
        vulList = vulTable.sort_by_risk()
        for vul in vulList:
            if len(vul.vul_list) == 0: continue
            Printer.print_risk_color(
                text="s" + str(vul.id) + ":" + vul.name, 
                risk=vul.risk
            )
            print("Descreibe: {}".format(vul.descreibe))
            print("Advice: {}".format(vul.advice))
            print("Detail: https://swcregistry.io/docs/SWC-{}\n".format(str(vul.id)))
            Printer._code_snippet(vul)
            print("\n")
        
    @staticmethod
    def _code_snippet(vuls:Vuls):
        for vul in vuls.vul_list:
            fileName = vul.fileName
            Printer.print_blue("\n{}\n".format(vul.fileName))
            for loc in vul.locList:
                with open(vul.fileName, "r", encoding="utf-8") as f:
                    codeLines = [line.split("\n")[0] for line in f.readlines()]
                if fileName != vul.fileName: Printer.print_blue("\n{}".format(vul.fileName))
                start = loc["start"]["line"]
                end = loc["end"]["line"]
                if start == 1: 
                    top = 0 
                else: 
                    top = start -2
                if end > len(codeLines):
                    bottom = len(codeLines)
                else:
                    bottom = end
                for lineIndex, codeLine in enumerate(codeLines[top:bottom+1]):
                    line = top + lineIndex
                    if line == top or line == bottom:
                        print("{}|".format(str(line+1)).rjust(7) + codeLine)
                    else:
                        Printer.print_yellow(">{}|".format(str(line+1)).rjust(7) + codeLine)
                print("\n")
                        
    @staticmethod
    def print_file_num(num:int):
        print("Contract files: " + Color.GREEN + str(num) + Color.END)
        
    def print_risk_color(text:str, risk:int):
        if risk == 0:
            print(text)
        elif risk == 1:
            Printer.print_green(text)
        elif risk == 2:
            Printer.print_yellow(text)
        elif risk == 3:
            Printer.print_red(text)
    
    @staticmethod
    def print_green(text):
        print(Color.GREEN + str(text) + Color.END)  

    @staticmethod
    def print_red(text):
        print(Color.RED + str(text) + Color.END)

    @staticmethod
    def print_blue(text):
        print(Color.BLUE + str(text) + Color.END)
        
    @staticmethod
    def print_yellow(text):
        print(Color.YELLOW + str(text) + Color.END)


class Color:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    END = "\033[0m"
    
    
if __name__ == "__main__":
    Printer.print_banner()
    Printer.print_file_num(10)