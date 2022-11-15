import os
import sys
import logging
from multiprocessing import Pool

from vuls import all_detector
from vuls.vul import VulTable
from solidity_antlr4_parser.parser import parse_file, objectify
from ast_scanner.ast_scanner import Scanner
from scraper.scraper import Scraper
from .utils import check_address

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
allDetectorList.sort()

class Asuka(object):
    """
        This is Asuka class which is core of detect vuls.
    """
    
    def __init__(self, _root:str, _detectors=allDetectorList, _threads=4, _chainType=None, _apiKey=None):
        """ init Asuka Object

        Args:
            _root (str): path of all solidity files.
            _detectors (_type_, optional): the detector you want to load. 
                Defaults to allDetectorList.
            _threads (int, optional): threads of scanning files. Defaults to 4.
            _chainType (str): like ETH, BSC etc.
        """
        self.root = _root
        self.detectors = _detectors
        self.thread = _threads
        self.chainType = _chainType
        self.apiKey = _apiKey
        self.allSolFiles = self._get_all_sol_files(_root)
        self.vulList = list()
        self.vulTable = VulTable(_detectors)
        
    def _is_sol_file(self, path:str) -> bool:
        """check the file of path is solidity file.

        Args:
            path (str): path of a single solidity file.

        Returns:
            bool: result.
        """
        # check the path has suffix ".sol"
        if path[-4:] != ".sol":
            return False
        # check the file is empty
        with open(path, "r", encoding="utf-8") as f:
            if len(f.readlines()) == 0:
                return False
        return True
    
    def _get_all_sol_files(self, path:str) -> list:
        """get all solidty file from a path

        Args:
            path (str): It can be a folder of a single solidity file.

        Raises:
            ValueError: Can't found any solidity files.

        Returns:
            list: A list of all solidity files.
        """
        if check_address(address=path) \
            and self.chainType \
                and self.apiKey:
            scraper = Scraper(chainType=self.chainType, apiKey=self.apiKey)
            path = scraper.get_source_code(address=path)
        
        if path[-4:] == ".sol":
            if self._is_sol_file(path):
                return [path]

        if path[-1] != "/": path += "/"
        
        allSolFiles = list()
        for root, dirs, files in os.walk(path):
            for _file in files:
                absFilePath = os.path.join(root, _file)
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
        """Scan a single solidity file.

        Args:
            param (tuple[str, list]): solidity file path 
                and list of vuls want to detect.
                
        Returns:
            list: vul list
        """
        solFilePath, detetors = param
        try:
            """
                parse solidity source code to an AST object 
                by using solidity_antlr4_parser module.
            """
            sourceUnit = parse_file(path=solFilePath, loc=True)
            sourceUnitObject = objectify(sourceUnit, file_name=solFilePath)
        except Exception as e:
            logging.info("Parse file failed: {}".format(solFilePath))
            logging.exception(e)
            raise RuntimeError("Parse file failed: {}".format(solFilePath))
            
        try:
            """
                Scanning solidity AST object to get scanner object
                by using ast_scanner moudule.
            """
            scanner = Scanner(sourceUnitObject)
        except Exception as e:
            logging.info("Scan ast failed: {}".format(solFilePath))
            logging.exception(e)
            raise RuntimeError("Scan ast failed: {}".format(solFilePath))
            
        vulList = list()
        for vulId in detetors:
            """
                Get all detectors by allDetectorTable.
                Using detectors to detect vuls.
            """
            detector = allDetectorTable[vulId]
            try:
                vulList.append(detector.check(scanner))
            except Exception as e:
                logging.info("Detector failed: {}".format(detector.NAME))
                logging.info("Sol file: {}".format(solFilePath))
                logging.exception(e)
                raise RuntimeError("Detector failed: {}".format(detector.NAME))
        return vulList        
        

    def scan(self):
        """
            Asuka class main methed to detect vuls by multi threaded.
        """
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

            