"""Structural assertions for the AST scanner layer."""


class _NodeWithLoc:
    """Minimal stand-in for a scanner node carrying a loc."""

    def __init__(self, start_line, start_col, end_line, end_col):
        self.loc = {
            "start": {"line": start_line, "column": start_col},
            "end": {"line": end_line, "column": end_col},
        }


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


class TestControlFlowFixture:
    """flow.sol exercises if/while/for/try-catch, interfaces and unary ops."""

    def test_interface_is_collected(self, scan_fixture):
        scan = scan_fixture("flow.sol")
        assert len(scan.interfaces) == 1
        assert len(scan.contracts) == 1
        # bar, f, g and getList from the contract (interface excluded)
        assert len(scan.functions) == 4

    def test_if_while_for_statements(self, scan_fixture):
        function = scan_fixture("flow.sol").functions[1]
        types = {s.type for s in function.statements}
        assert "IfStatement" in types
        assert "WhileStatement" in types
        assert "ForStatement" in types

    def test_try_catch_statements(self, scan_fixture):
        function = scan_fixture("flow.sol").functions[0]
        types = {s.type for s in function.statements}
        # note: "TryStatment" is the visitor's historical spelling
        assert "TryStatment" in types
        assert "CatchClause" in types

    def test_unary_and_binary_expressions(self, scan_fixture):
        function = scan_fixture("flow.sol").functions[1]
        assert function.operators  # binary ops from loop arithmetic
        # unary i++/j-- contribute their sub-expressions
        assert any(e.type == "Identifier" and e.name == "j"
                   for e in function.expressions)

    def test_single_statement_for_body(self, scan_fixture):
        """A for-loop body without braces still contributes statements."""
        function = scan_fixture("flow.sol").functions[2]  # g()
        assert any(
            e.type == "Identifier" and e.name == "sum"
            for e in function.expressions
        )

    def test_index_access_on_call_result(self, scan_fixture):
        """getList()[0] - IndexAccess whose base is a FunctionCall.

        The fallback name is the base node type itself ("FunctionCall").
        """
        function = scan_fixture("flow.sol").functions[2]  # g()
        assert any(
            e.type == "IndexAccess" and e.name == "FunctionCall"
            for e in function.expressions
        )


class TestTools:
    def test_scope_check_loop_contains_msg_value(self, scan_file):
        from ast_scanner.ast_scanner import Tools

        function = scan_file("msgvalue_in_loop.sol").functions[0]
        for_stmt = next(
            s for s in function.statements if s.type == "ForStatement"
        )
        msg_value = next(
            e for e in function.expressions
            if e.type == "Identifier" and e.name == "msg"
        )
        assert Tools.scope_check(for_stmt, msg_value)

    def test_scope_check_same_line_contained(self):
        """Outer (cols 0-50) fully contains inner (cols 10-20) on line 5.

        This branch used to crash with AttributeError: loc dicts were
        accessed with attribute syntax instead of keys.
        """
        from ast_scanner.ast_scanner import Tools

        outer = _NodeWithLoc(5, 0, 5, 50)
        inner = _NodeWithLoc(5, 10, 5, 20)
        assert Tools.scope_check(outer, inner)

    def test_scope_check_same_line_not_contained(self):
        from ast_scanner.ast_scanner import Tools

        outer = _NodeWithLoc(5, 0, 5, 50)
        inner = _NodeWithLoc(5, 60, 5, 70)
        assert not Tools.scope_check(outer, inner)

    def test_scope_check_multiline_contained(self):
        from ast_scanner.ast_scanner import Tools

        outer = _NodeWithLoc(1, 0, 10, 0)
        inner = _NodeWithLoc(5, 0, 6, 0)
        assert Tools.scope_check(outer, inner)

    def test_scope_check_multiline_disjoint(self):
        from ast_scanner.ast_scanner import Tools

        outer = _NodeWithLoc(1, 0, 2, 0)
        inner = _NodeWithLoc(8, 0, 9, 0)
        assert not Tools.scope_check(outer, inner)

    def test_check_modifier_matches(self, scan_fixture):
        from ast_scanner.ast_scanner import Tools

        scan = scan_fixture("negative_calls.sol")
        function = next(
            f for f in scan.functions
            if f.functionObject.visibility == "external"
        )
        # getInfo() is external view: stateMutability counts as a modifier
        assert Tools.check_modifier(
            function.functionObject, ["onlyOwner", "view"]
        ) == ["view"]

    def test_check_modifier_no_match(self, scan_fixture):
        from ast_scanner.ast_scanner import Tools

        scan = scan_fixture("negative_calls.sol")
        function = next(
            f for f in scan.functions if f.functionObject.visibility == "public"
        )
        assert not Tools.check_modifier(
            function.functionObject, ["onlyOwner", "onlyGov"]
        )


class TestGetBelowStatements:
    def test_returns_statements_at_or_after_node(self, scan_file):
        scan = scan_file("reentrancy.sol")
        # the low-level call is `msg.sender.call.value(amount)()`,
        # whose FunctionCall expression is named "value"
        function = next(
            f for f in scan.functions
            if any(c.name == "value" for c in f.functionCalls)
        )
        call = next(c for c in function.functionCalls if c.name == "value")
        below = function.get_below_statements(call)
        assert below  # storage decl + member write follow the call
        assert all(
            s.loc["start"]["line"] >= call.loc["start"]["line"] for s in below
        )

    def test_node_without_loc_returns_empty(self, scan_file):
        function = scan_file("reentrancy.sol").functions[0]
        assert function.get_below_statements({}) == []
