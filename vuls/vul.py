class Vuls(object):
    
    def __init__(self, name:str, id:int, descreibe:str, advice:str, risk:int, vulList:list):
        self.name = name
        self.id = id
        self.descreibe = descreibe
        self.advice = advice
        self.vul_list = vulList
        self.risk = risk
        
    def vul_count(self) -> int:
        return len(self.vul_list)
        
    def __add__(self, _vuls):
        "merge all same type vul from different files"
        if not hasattr(_vuls, "id"):
            raise ValueError("There is no name attr!")
        if self.id == _vuls.id:
            self.vul_list += _vuls.vul_list
        else:
            raise ValueError("Wrong vul type!")
        return self
            
        
class Vul(object):
    
    def __init__(self, fileName:str, locList:list):
        self.fileName = fileName
        self.locList = locList
        

class VulTable(dict):
    
    def __init__(self, _detectors):
        for detector in _detectors:
            self[detector] = None
        
    def __add__(self, _vuls:Vuls):
        if not self[_vuls.id]:
            self[_vuls.id] = _vuls
        else:
            self[_vuls.id] += _vuls
        return self
    
    def count_table(self) -> dict:
        countTable = {3: 0, 2: 0, 1: 0, 0: 0}
        for vuls in self.values():
            countTable[vuls.risk] += vuls.vul_count()
        return countTable
    
    def vul_count(self) -> int:
        count = 0
        for vuls in self.values():
            count += vuls.vul_count()
        return count
    
    def sort_by_risk(self) -> list:
        vulList = sorted(
                [
                    vul for vul in self.values()
                ], 
                key=lambda x : x.risk, 
                reverse=True
            )
        return vulList


class Color:
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    END = "\033[0m"


Risk = {
    0:"Info",
    1:Color.BLUE + "Low" + Color.END,
    2:Color.YELLOW + "Medium" + Color.END,
    3:Color.RED + "High" + Color.END
}
