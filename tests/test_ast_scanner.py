"""Structural assertions for the AST scanner layer."""


def test_filters_contracts_and_functions(scan_file):
    scan = scan_file("test.sol")
    assert len(scan.contracts) == 8
    assert len(scan.interfaces) == 0
    assert len(scan.functions) == 19


def test_bec_token_layout(scan_file):
    scan = scan_file("bec.sol")
    assert len(scan.contracts) == 8
    assert len(scan.functions) == 19


def test_delegatecall_function(scan_file):
    scan = scan_file("delegatecall.sol")
    assert len(scan.contracts) == 1
    assert len(scan.functions) == 1

    function = scan.functions[0]
    assert any(call.name == "delegatecall" for call in function.functionCalls)
    assert function.statements
    assert function.expressions


def test_msgvalue_in_loop_structure(scan_file):
    scan = scan_file("msgvalue_in_loop.sol")
    function = scan.functions[0]

    assert any(s.type == "ForStatement" for s in function.statements)
    assert any(
        e.type == "MemberAccess" and e.name == "value"
        for e in function.expressions
    )
    # arithmetic inside the loop shows up as operators
    assert function.operators


def test_modifier_collection(scan_file):
    scan = scan_file("reentrancy.sol")
    modifiers = {
        m for f in scan.functions for m in f.modifiers
    }
    # payable is a stateMutability, not a modifier node
    assert modifiers == {"nonReentrant"}
