import logging
import os
from multiprocessing import Pool

from ast_scanner.ast_scanner import Scanner
from scraper.scraper import Scraper
from solidity_antlr4_parser.parser import objectify, parse_file
from vuls.all_detector import ALL_DETECTORS, DETECTOR_IDS
from vuls.vul import VulTable

from .utils import check_address


class Asuka:
    """
        This is Asuka class which is core of detect vuls.
    """

    def __init__(self, _root="", _detectors=DETECTOR_IDS, _threads=4, _chainType=None, _apiKey=None):
        """ init Asuka Object

        Args:
            _root (str): path of all solidity files.
            _detectors (list[int], optional): the detector ids you want to run.
                Defaults to DETECTOR_IDS from vuls.all_detector.
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
        self.errors = list()

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
        with open(path, encoding="utf-8") as f:
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
        if not path:
            return list()

        if check_address(address=path) \
            and self.chainType \
                and self.apiKey:
            scraper = Scraper(chainType=self.chainType, apiKey=self.apiKey)
            path = scraper.get_source_code(address=path)

        if not os.path.exists(path):
            raise ValueError(f"Path not found: {path}")

        if path[-4:] == ".sol":
            if self._is_sol_file(path):
                return [path]
            raise ValueError(f"Invalid or empty solidity file: {path}")

        if os.path.isfile(path):
            raise ValueError(f"Not a solidity file: {path}")

        if path[-1] != "/":
            path += "/"

        allSolFiles = list()
        for root, _dirs, files in os.walk(path):
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
        return self.vulTable.vul_count()

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
            sourceUnit = parse_file(path=solFilePath, loc=True, strict=True)
            sourceUnitObject = objectify(sourceUnit, file_name=solFilePath)
        except Exception as e:
            logging.info(f"Parse file failed: {solFilePath}")
            logging.exception(e)
            raise RuntimeError(f"Parse file failed: {solFilePath}") from e

        try:
            """
                Scanning solidity AST object to get scanner object
                by using ast_scanner moudule.
            """
            scanner = Scanner(sourceUnitObject)
        except Exception as e:
            logging.info(f"Scan ast failed: {solFilePath}")
            logging.exception(e)
            raise RuntimeError(f"Scan ast failed: {solFilePath}") from e

        vulList = list()
        for vulId in detetors:
            """
                Get all detectors by ALL_DETECTORS.
                Using detectors to detect vuls.
            """
            detector = ALL_DETECTORS[vulId]
            try:
                vulList.append(detector.check(scanner))
            except Exception as e:
                logging.info(f"Detector failed: {detector.NAME}")
                logging.info(f"Sol file: {solFilePath}")
                logging.exception(e)
                raise RuntimeError(f"Detector failed: {detector.NAME}") from e
        return vulList


    def _scan_file_isolated(self, param: tuple[str, list]) -> tuple:
        """Run scan_file, converting any failure into an error report.

        A single broken file must never abort the whole scan; failures
        are collected into scan results and surfaced by Asuka.errors.

        Args:
            param (tuple[str, list]): same signature as scan_file.

        Returns:
            tuple: (vulList, None) on success, (None, errorMessage) on failure.
        """
        try:
            return self.scan_file(param), None
        except Exception as e:
            return None, f"{param[0]}: {e}"

    def scan(self):
        """
            Asuka class main methed to detect vuls by multi threaded.
        """
        pool = Pool(processes=self.thread)
        results = pool.map(
            self._scan_file_isolated,
            [(solFilePath, self.detectors) for solFilePath in self.allSolFiles]
        )
        pool.close()
        pool.join()

        self.errors = list()
        for vulList, error in results:
            if error is not None:
                self.errors.append(error)
                continue
            for vul in vulList:
                self.vulTable += vul

