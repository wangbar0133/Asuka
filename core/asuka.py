import os
import logging
from multiprocessing import Pool

from vuls import all_detector
from vuls.vul import VulTable
from solidity_antlr4_parser.parser import parse_file, objectify
from ast_scanner.ast_scanner import Scanner

logging.basicConfig(
    filename="debug.log", 
    filemode="w", 
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
    datefmt="%d-%M-%Y %H:%M:%S",
    level=logging.DEBUG
)

# load all detector
allDetectorTable = dict()
allDetectorList = list()
for attrName in dir(all_detector):
    if hasattr(getattr(all_detector, attrName), "check"):
        detetor = getattr(all_detector, attrName)
        allDetectorTable[detetor.ID] = detetor
        allDetectorList.append(detetor.ID)


class Asuka(object):
    
    def __init__(self, _root:str, _detectors=allDetectorList, _threads=4):
        self.root = _root
        self.detectors = _detectors
        self.thread = _threads
        self.allSolFiles = self._get_all_sol_files(_root)
        self.vulList = list()
        self.vulTable = VulTable()
        
    def _is_sol_file(self, path:str) -> bool: 
        if path[-4:] != ".sol":
            return False
        with open(path, "r", encoding="utf-8") as f:
            if len(f.readlines()) == 0:
                return False
        return True
    
    def _get_all_sol_files(self, path:str) -> list:
        if path[-4:] == ".sol":
            if self._is_sol_file(path):
                return [path]

        if path[-1] != "/": path += "/"
        
        allSolFiles = list()
        for root, dirs, files in os.walk(path):
            for _file in files:
                absFilePath = root + "/" + _file
                if self._is_sol_file(absFilePath):
                    allSolFiles.append(absFilePath)
        if len(allSolFiles) == 0:
            raise ValueError("Solidity file not found!")
        
        return allSolFiles
        
    def file_count(self) -> int:
        return len(self.allSolFiles)
    
    def vul_count(self) -> int:
        return len(self.vulList)    
        
    def scan_file(self, param:tuple[str, list]) -> list:
        solFilePath, detetors = param
        try:
            sourceUnit = parse_file(path=solFilePath, loc=True)
            sourceUnitObject = objectify(sourceUnit)
        except Exception as e:
            logging.info("Parse file failed: {}".format(solFilePath))
            logging.exception(e)
            
        try:
            scanner = Scanner(sourceUnitObject)
        except Exception as e:
            logging.info("Scan ast failed: {}".format(solFilePath))
            logging.exception(e)
            
        vulList = list()
        for vulId in detetors:
            detector = allDetectorTable[vulId]
            try:
                vulList.append(detector.check(scanner))
            except Exception as e:
                logging.info("Detector failed: {}".format(detector.NAME))
                logging.info("Sol file: {}".format(solFilePath))
                logging.exception(e)
        return vulList        
        

    def scan(self):
        pool = Pool(processes=self.thread)
        vulLists = pool.map(
            self.scan_file,
            [(solFilePath, self.detectors) for solFilePath in self.allSolFiles]
        )
        pool.close()
        pool.join()
        
        for vulList in vulLists:
            for vul in vulList:
                self.vulTable += vul
            

            