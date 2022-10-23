class Vuls(object):
    
    def __init__(self, name:str, id:int, descreibe:str, advice:str, risk:int, vulList:list):
        self.name = name
        self.id = id
        self.descreibe = descreibe
        self.advice = advice
        self.vul_list = vulList
        self.risk = risk
        
    def vul_count(self) -> int:
        return len(self.vul)
        
    def add(self, _vuls):
        "merge all same type vul from different files"
        if not hasattr(_vuls, "name"):
            raise ValueError("There is no name attr!")
        if self.id == _vuls.name:
            self.vul_list += _vuls.vul_list
        else:
            raise ValueError("Wrong vul type!")
            
        
class Vul(object):
    
    def __init__(self, fileName, locList):
        self.fileName = fileName
        self.locList = locList
        

class VulTable(dict):
                
    def __add__(self, _vuls:Vuls):
        if not _vuls.id in self.keys():
            self[_vuls.id] = _vuls
        else:
            self[_vuls.id].vul_list += _vuls.vul_list
        return self