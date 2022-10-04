class Vuls(object):
    
    def __init__(self, name, id, descreibe, advice, risk, vulList):
        self.name = name
        self.id = id
        self.descreibe = descreibe
        self.advice = advice
        self.vul_list = vulList
        self.risk = risk
        self.hasVuls = False
        if self.vul_list:
            self.hasVuls = True
            
        
class Vul(object):
    
    def __init__(self, fileName, locList):
        self.fileName = fileName
        self.locList = locList