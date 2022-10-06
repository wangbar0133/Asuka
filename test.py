import unittest

class TestScanner(unittest.TestCase):

    def test_ast_scanner(self):
        from solidity_antlr4_parser.parser import parse_file, objectify
        from ast_scanner.ast_scanner import Scanner
        path = "/Users/wang/dev/Asuka/test_data/test.sol"
        source_unit = parse_file(path, loc=True)
        source_unit_object = objectify(source_unit, path)
        scanner = Scanner(source_unit_object)
        pass
    
class TestVuls(unittest.TestCase):
    
    def test_int_overflow(self):
        from solidity_antlr4_parser.parser import parse_file, objectify
        from ast_scanner.ast_scanner import Scanner
        from vuls.int_overflow import check
        path = "/Users/wang/dev/Asuka/test.sol"
        source_unit = parse_file(path, loc=True)
        source_unit_object = objectify(source_unit, path)
        scanner = Scanner(source_unit_object)
        vuls = check(scanner)
        pass
    
    def test_check_solc_version(self):
        from vuls.int_overflow import check_solc_version
        self.assertEqual(True, check_solc_version("<=0.8.0", 8))
        self.assertEqual(False, check_solc_version("^0.8.0", 8))
        self.assertEqual(False, check_solc_version("0.8.0", 8))
        self.assertEqual(True, check_solc_version("<0.8.0", 8))
        self.assertEqual(True, check_solc_version("<0.7.0", 8))
        self.assertEqual(True, check_solc_version("^0.7.0", 8))
        self.assertEqual(True, check_solc_version("0.4.0", 8))
        
    def test_function_default_visibility(self):
        from solidity_antlr4_parser.parser import parse_file, objectify
        from ast_scanner.ast_scanner import Scanner
        from vuls.function_default_visibility import check
        path = "/Users/wang/dev/Asuka/test1.sol"
        source_unit = parse_file(path, loc=True)
        source_unit_object = objectify(source_unit, path)
        scanner = Scanner(source_unit_object)
        vuls = check(scanner)
        pass
    
    def test_unchecked_return_value(self):
        from solidity_antlr4_parser.parser import parse_file, objectify
        from ast_scanner.ast_scanner import Scanner
        from vuls.unchecked_return_value import check
        path = "/Users/wang/dev/Asuka/test1.sol"
        source_unit = parse_file(path, loc=True)
        source_unit_object = objectify(source_unit, path)
        scanner = Scanner(source_unit_object)
        vuls = check(scanner)
        pass
    
    def test_reentrancy(self):
        from solidity_antlr4_parser.parser import parse_file, objectify
        from ast_scanner.ast_scanner import Scanner
        from vuls.reentrancy import check
        path = "/Users/wang/dev/Asuka/test_data/reentrancy.sol"
        source_unit = parse_file(path, loc=True)
        source_unit_object = objectify(source_unit, path)
        scanner = Scanner(source_unit_object)
        vuls = check(scanner)
        pass