"""AST scanning layer: turns objectified parser output into the
Scanner/Contract/Function model consumed by detectors."""

from solidity_antlr4_parser.parser import Node


class Expression(dict):
    """Dict with attribute access; missing keys yield None."""

    def __getattr__(self, key: str):
        return self.get(key)

    def __setattr__(self, key: str, value) -> None:
        self[key] = value


class Scanner:
    """
        A class to scanning solidity unit object.
    """

    def __init__(self, sourceUnitObject: Node):
        self.sourceUnitObject = sourceUnitObject
        self.fileName: str = self.sourceUnitObject.fileName
        self.contracts: list[Contract] = []
        self.interfaces: list[Node] = []
        self.functions: list[Function] = []
        self.operators: list[Expression] = []

        self.filter_contracts()
        self.get_functions()
        self.get_operators()

    def filter_contracts(self) -> None:
        for contractObject in self.sourceUnitObject.contracts.values():
            if contractObject.kind == "interface":
                self.interfaces.append(contractObject)

            elif contractObject.kind == "contract":
                self.contracts.append(Contract(contractObject))

    def get_functions(self) -> None:
        for contract in self.contracts:
            self.functions += contract.functions

    def get_operators(self) -> None:
        for function in self.functions:
            self.operators += function.operators


class Contract:

    def __init__(self, contractObject: Node):
        self.contractObject = contractObject
        self.functions: list[Function] = []
        self.get_functions()

    def get_functions(self) -> None:
        if self.contractObject.functions:
            for functionObject in self.contractObject.functions.values():
                self.functions.append(Function(functionObject))


class Function:

    def __init__(self, functionObject):
        self.functionObject = functionObject
        self.modifiers: list[str] = []
        self.statements: list[Node] = []
        self.expressions: list[Expression] = []
        self.functionCalls: list[Expression] = []
        self.variables: list[Expression] = []
        self.numberLiteral: list[Expression] = []
        self.variableDeclaration: list = []
        self.operators: list[Expression] = []

        self.get_modifier()
        self.get_statements()
        self.get_expressions()
        self.get_variables()
        self.get_number_literals()
        self.get_variable_declarations()
        self.get_operators()
        self.get_function_calls()

    def get_modifier(self) -> None:
        self.modifiers = [mod.name for mod in self.functionObject.node.modifiers]

    def get_statements(self) -> None:
        if self.functionObject.node.body:
            for statement in self.functionObject.node.body.statements:
                self.visit_statement(statement)

    def visit_statement(self, statement) -> None:
        if statement:
            self.statements.append(statement)
            if statement.type == "IfStatement":
                self.visit_statement(statement.condition)
                self.visit_statement(statement.TrueBody)
                self.visit_statement(statement.FalseBody)

            elif statement.type == "WhileStatement":
                self.visit_statement(statement.condition)

            elif statement.type == "ForStatement":
                self.visit_statement(statement.initExpression)
                self.visit_statement(statement.conditionExpression)
                self.visit_statement(statement.loopExpression)
                if statement.body.type == "Block":
                    if statement.body.statements:
                        for state in statement.body.statements:
                            self.visit_statement(state)
                else:
                    self.visit_statement(statement.body)

            elif statement.type == "Block":
                for block_statement in statement.statements:
                    self.visit_statement(block_statement)

            elif statement.type == "TryStatment":
                self.visit_statement(statement.block)
                self.visit_statement(statement.expression)
                for catchClause in statement.catchClause:
                    self.visit_statement(catchClause)

            elif statement.type == "CatchClause":
                self.visit_statement(statement.block)

            else:
                pass

    def get_expressions(self) -> None:
        if self.statements:
            for statement in self.statements:
                self.get_expression(statement)

    def get_expression(self, expressionObject) -> None:
        if expressionObject.type == "Identifier":
            self.expressions.append(
                Expression(
                    {
                        "name": expressionObject.name,
                        "loc": expressionObject.loc,
                        "type": expressionObject.type
                    }
                )
            )

        elif expressionObject.type == "VariableDeclarationStatement":
            if expressionObject.variables:
                for variable_declaration in expressionObject.variables:
                    self.expressions.append(
                        Expression(
                            {
                                "name": variable_declaration.name,
                                "loc": variable_declaration.loc,
                                "type": variable_declaration.type,
                                "type_name": variable_declaration.typeName
                            }
                        )
                    )
            if expressionObject.initialValue:
                self.get_expression(expressionObject.initialValue)

        elif expressionObject.type == "MemberAccess":
            self.expressions.append(
                Expression(
                    {
                        "name": expressionObject.memberName,
                        "loc": expressionObject.loc,
                        "type": expressionObject.type,
                        "expression": expressionObject.expression
                    }
                )
            )
            self.get_expression(expressionObject.expression)

        elif expressionObject.type == "IndexAccess":
            if expressionObject.base.type == "MemberAccess":
                name = expressionObject.base.memberName
            elif expressionObject.base.type == "Identifier":
                name = expressionObject.base.name
            else:
                name = expressionObject.base.type
            self.expressions.append(
                Expression(
                    {
                        "name": name,
                        "loc": expressionObject.loc,
                        "type": expressionObject.type,
                        "base": expressionObject.base,
                        "index": expressionObject.index
                    }
                )
            )
            self.get_expression(expressionObject.base)
            self.get_expression(expressionObject.index)

        elif expressionObject.type == "BinaryOperation":
            self.expressions.append(
                Expression(
                    {
                        "name": expressionObject.operator,
                        "loc": expressionObject.loc,
                        "type": expressionObject.type,
                        "operator": expressionObject.operator
                    }
                )
            )
            self.get_expression(expressionObject.left)
            self.get_expression(expressionObject.right)

        elif expressionObject.type == "NumberLiteral":
            self.expressions.append(
                Expression(
                    {
                        "name": expressionObject.number,
                        "loc": expressionObject.loc,
                        "type": expressionObject.type
                    }
                )
            )

        elif expressionObject.type == "FunctionCall":
            if expressionObject.expression:
                if expressionObject.expression.type == "MemberAccess":
                    self.expressions.append(
                        Expression(
                            {
                                "name": expressionObject.expression.memberName,
                                "loc": expressionObject.loc,
                                "type": expressionObject.type,
                                "arguments": expressionObject.arguments,
                                "expression": expressionObject.expression.expression
                            }
                        )
                    )
                    self.get_expression(expressionObject.expression.expression)
                    for argument in expressionObject.arguments:
                        self.get_expression(argument)

                elif expressionObject.expression.type == "Identifier":
                    self.expressions.append(
                        Expression(
                            {
                                "name": expressionObject.expression.name,
                                "loc": expressionObject.loc,
                                "type": expressionObject.type,
                                "arguments": expressionObject.arguments,
                            }
                        )
                    )
                    for argument in expressionObject.arguments:
                        self.get_expression(argument)

                else:
                    # any other callee shape (e.g. the TypeNameExpression
                    # of an elementary cast like uint8(...)); the call
                    # itself is not recorded, but its arguments must
                    # still be visited - calls inside casts used to be
                    # invisible to the Scanner
                    self.get_expression(expressionObject.expression)
                    for argument in expressionObject.arguments:
                        self.get_expression(argument)

        elif expressionObject.type == "ExpressionStatement":
            self.get_expression(expressionObject.expression)

        elif expressionObject.type == "UnaryOperation":
            self.get_expression(expressionObject.subExpression)

    def get_variables(self) -> None:
        if self.expressions:
            for expression in self.expressions:
                if expression["type"] == "Identifier":
                    self.variables.append(expression)

    def get_number_literals(self) -> None:
        if self.expressions:
            for expression in self.expressions:
                if expression["type"] == "NumberLiteral":
                    self.numberLiteral.append(expression)

    def get_variable_declarations(self) -> None:
        if self.expressions:
            for expression in self.expressions:
                if expression["type"] == "VariableDeclaration":
                    self.variableDeclaration.append(expression)

        for declaration in self.functionObject.declarations.values():
            if declaration.type == "VariableDeclaration":
                self.variableDeclaration.append(declaration)

    def get_operators(self) -> None:
        if self.expressions:
            for expression in self.expressions:
                if expression["type"] == "BinaryOperation":
                    self.operators.append(expression)

    def get_function_calls(self) -> None:
        if self.expressions:
            for expression in self.expressions:
                if expression["type"] == "FunctionCall":
                    self.functionCalls.append(expression)

    def get_below_statements(self, node) -> list[Node]:
        below_statements: list[Node] = []
        # Node.__getattr__ raises KeyError for missing keys, which
        # hasattr() does not catch - use the dict interface instead.
        if not node.get("loc"):
            return below_statements
        nodeStartLine = node.loc["start"]["line"]
        for statement in self.statements:
            if statement.loc["start"]["line"] >= nodeStartLine:
                below_statements.append(statement)
        return below_statements


class Tools:

    @staticmethod
    def scope_check(ctx0, ctx1) -> bool:
        loc0 = ctx0.loc
        loc1 = ctx1.loc
        if loc0["start"]["line"] == loc1["start"]["line"] \
            and loc0["end"]["line"] == loc1["end"]["line"] \
                and loc0["start"]["line"] == loc0["end"]["line"]:
                    # both nodes on one line: compare columns.
                    # (attribute access on plain dicts used to crash here,
                    # and the end-column comparison was a copy-paste of the
                    # start comparison)
                    if loc0["start"]["column"] <= loc1["start"]["column"] \
                        and loc0["end"]["column"] >= loc1["end"]["column"]:
                            return True
                    else:
                        return False
        elif loc0["start"]["line"] < loc1["start"]["line"] \
            and loc0["end"]["line"] > loc1["end"]["line"]:
                return True
        else:
            return False

    @staticmethod
    def check_modifier(function_object, modifier: list[str]) -> list[str]:
        """Checking if a function declaration contains certain modifiers"""
        mod_list: list[str] = []
        function_modifier_list = [mod["name"] for mod in function_object.node["modifiers"]]
        if hasattr(function_object, "stateMutability") and function_object.stateMutability:
            function_modifier_list.append(function_object.stateMutability)

        if hasattr(function_object, "visibility") and function_object.visibility:
            function_modifier_list.append(function_object.visibility)

        for mod in function_modifier_list:
            for modif in modifier:
                if modif in mod:
                    mod_list.append(mod)

        return list(set(mod_list))

    @staticmethod
    def iter_nodes(node):
        """Yield node and every AST node nested inside it.

        Walks raw parser Nodes by their dict values, so any expression
        shape (binary ops, calls, member accesses, tuples, ...) is
        covered without enumerating grammar rules.
        """
        if not isinstance(node, dict) or "type" not in node:
            return
        yield node
        for value in node.values():
            if isinstance(value, dict):
                yield from Tools.iter_nodes(value)
            elif isinstance(value, list):
                for item in value:
                    yield from Tools.iter_nodes(item)
