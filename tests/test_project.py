"""Cross-file project model: import resolution, symbol table, edge cases."""
from pathlib import Path

from core.project import EXTERNAL, MISSING, RESOLVED, ImportSpec, Project
from tests.conftest import FIXTURES

PROJECT_DIR = FIXTURES / "project"
MAIN = PROJECT_DIR / "main.sol"


def load_main() -> Project:
    return Project.load([MAIN], root=PROJECT_DIR)


class TestImportResolution:
    def test_relative_chain_is_loaded(self):
        project = load_main()
        assert {path.name for path in project.files} == {
            "main.sol", "Base.sol", "Ownable.sol", "Token.sol", "IERC20.sol",
        }

    def test_import_kinds(self):
        project = load_main()
        main = project.files[MAIN.resolve()]
        assert [spec.kind for spec in main.imports] == [RESOLVED, RESOLVED]
        assert [spec.raw_path for spec in main.imports] == [
            "./lib/Base.sol", "./lib/Token.sol",
        ]

    def test_nested_parent_import(self):
        """Base.sol reaches ../../common/Ownable.sol."""
        project = load_main()
        base = project.files[(PROJECT_DIR / "lib" / "Base.sol").resolve()]
        assert base.imports[0].kind == RESOLVED
        assert base.imports[0].path == (PROJECT_DIR / "common" / "Ownable.sol").resolve()

    def test_root_relative_import(self, tmp_path):
        """A leading slash resolves against the project root."""
        (tmp_path / "lib").mkdir()
        (tmp_path / "lib" / "Token.sol").write_text(
            "pragma solidity ^0.8.0;\ncontract Token {}\n"
        )
        (tmp_path / "main.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "/lib/Token.sol";\ncontract Main {}\n'
        )
        project = Project.load([tmp_path / "main.sol"], root=tmp_path)
        assert (tmp_path / "lib" / "Token.sol").resolve() in project.files

    def test_imported_files_closure(self):
        project = load_main()
        imported = {
            path.name for path in project.imported_files(MAIN)
        }
        assert imported == {"Base.sol", "Ownable.sol", "Token.sol", "IERC20.sol"}

    def test_missing_relative_import(self, tmp_path):
        (tmp_path / "a.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./nope.sol";\ncontract A {}\n'
        )
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        spec = project.files[(tmp_path / "a.sol").resolve()].imports[0]
        assert spec.kind == MISSING
        assert project.missing_imports() == [
            ((tmp_path / "a.sol").resolve(), "./nope.sol")
        ]
        assert project.failed_files() == []

    def test_external_import_is_not_an_error(self, tmp_path):
        (tmp_path / "a.sol").write_text(
            'pragma solidity ^0.8.0;\n'
            'import "@openzeppelin/contracts/token/ERC20/IERC20.sol";\n'
            'contract A {}\n'
        )
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        spec = project.files[(tmp_path / "a.sol").resolve()].imports[0]
        assert spec.kind == EXTERNAL
        assert project.missing_imports() == []
        assert project.external_imports() == [
            ((tmp_path / "a.sol").resolve(),
             "@openzeppelin/contracts/token/ERC20/IERC20.sol")
        ]


class TestSymbols:
    def test_symbols_across_files(self):
        project = load_main()
        base_path, base = project.find_symbol("Base")
        assert base_path.name == "Base.sol"
        assert base.node.kind == "contract"

        ownable_path, _ = project.find_symbol("Ownable")
        assert ownable_path.name == "Ownable.sol"

    def test_libraries_and_interfaces_are_indexed(self):
        project = load_main()
        token_lib_path, token_lib = project.find_symbol("TokenLib")
        assert token_lib_path.name == "Token.sol"
        assert token_lib.node.kind == "library"

        interface_path, interface = project.find_symbol("IERC20")
        assert interface_path.name == "IERC20.sol"
        assert interface.node.kind == "interface"

    def test_unknown_symbol(self):
        assert load_main().find_symbol("Nope") is None

    def test_duplicate_symbols_are_reported(self, tmp_path):
        (tmp_path / "a.sol").write_text("pragma solidity ^0.8.0;\ncontract Dup {}\n")
        (tmp_path / "b.sol").write_text("pragma solidity ^0.8.0;\ncontract Dup {}\n")
        project = Project.load([tmp_path / "a.sol", tmp_path / "b.sol"], root=tmp_path)
        duplicates = project.duplicate_symbols()
        assert list(duplicates) == ["Dup"]
        assert {path.name for path in duplicates["Dup"]} == {"a.sol", "b.sol"}

    def test_symbol_names_per_file(self):
        project = load_main()
        assert project.files[(PROJECT_DIR / "lib" / "Token.sol").resolve()] \
            .symbol_names() == ["TokenLib"]


class TestRobustness:
    def test_import_cycle_terminates(self, tmp_path):
        (tmp_path / "a.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./b.sol";\ncontract A {}\n'
        )
        (tmp_path / "b.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./a.sol";\ncontract B {}\n'
        )
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        assert {path.name for path in project.files} == {"a.sol", "b.sol"}
        assert project.cycles  # a -> b -> a is recorded
        assert set(project.symbols) == {"A", "B"}

    def test_broken_import_is_tolerated(self, tmp_path):
        (tmp_path / "bad.sol").write_text("this is not solidity {{{ !!!")
        (tmp_path / "good.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./bad.sol";\ncontract Good {}\n'
        )
        project = Project.load([tmp_path / "good.sol"], root=tmp_path)
        bad = project.files[(tmp_path / "bad.sol").resolve()]
        assert not bad.ok
        assert "SyntaxError" in bad.error or "syntax error" in bad.error.lower()
        assert project.failed_files() == [bad]
        # the healthy file is still fully usable
        assert project.find_symbol("Good") is not None
        assert bad.symbol_names() == []

    def test_file_loaded_once_through_two_importers(self, tmp_path):
        (tmp_path / "shared.sol").write_text(
            "pragma solidity ^0.8.0;\ncontract Shared {}\n"
        )
        (tmp_path / "a.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./shared.sol";\ncontract A {}\n'
        )
        (tmp_path / "b.sol").write_text(
            'pragma solidity ^0.8.0;\nimport "./shared.sol";\ncontract B {}\n'
        )
        project = Project.load(
            [tmp_path / "a.sol", tmp_path / "b.sol"], root=tmp_path
        )
        shared = (tmp_path / "shared.sol").resolve()
        assert list(project.files).count(shared) == 1
        assert len(project.symbols["Shared"]) == 1

    def test_empty_import_path(self, tmp_path):
        (tmp_path / "a.sol").write_text("pragma solidity ^0.8.0;\ncontract A {}\n")
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        assert project.resolve_import("", tmp_path / "a.sol") == (None, MISSING)


class TestCachedLoader:
    def test_project_for_memoises(self, tmp_path):
        from core.project import clear_project_cache, project_for

        clear_project_cache()
        (tmp_path / "a.sol").write_text("pragma solidity ^0.8.0;\ncontract A {}\n")
        first = project_for(tmp_path, [tmp_path / "a.sol"])
        second = project_for(tmp_path, [tmp_path / "a.sol"])
        assert first is second
        clear_project_cache()


class TestDebugHelpers:
    def test_import_spec_repr_and_flag(self):

        resolved = ImportSpec("./x.sol", {}, Path("/tmp/x.sol"), RESOLVED)
        assert resolved.is_resolved
        assert "x.sol" in repr(resolved)
        assert "resolved" in repr(resolved)

        missing = ImportSpec("./y.sol", {}, None, MISSING)
        assert not missing.is_resolved

    def test_source_file_repr_and_name(self, tmp_path):
        from core.project import SourceFile

        plain = SourceFile(tmp_path / "a.sol")
        assert plain.name == "a.sol"
        assert "unloaded" in repr(plain)

        plain.error = "boom"
        assert "error='boom'" in repr(plain)

    def test_project_repr(self):
        text = repr(load_main())
        assert "files=" in text
        assert "symbols=" in text


class TestCrossFileInheritance:
    """Scanner/Contract resolution through the project."""

    def _scan_main(self):
        from ast_scanner.ast_scanner import Scanner
        from solidity_antlr4_parser.parser import objectify, parse_file

        project = load_main()
        tree = objectify(parse_file(str(MAIN), loc=True, strict=True), str(MAIN))
        return Scanner(tree, project=project).contracts[0]

    def test_base_names(self):
        assert self._scan_main().base_names == ["Base"]

    def test_resolved_state_vars_span_three_files(self):
        """value (main.sol) + baseValue (Base.sol) + owner (Ownable.sol)."""
        contract = self._scan_main()
        assert list(contract.contractObject.stateVars) == ["value"]
        assert sorted(contract.resolved_state_vars()) == [
            "baseValue", "owner", "value",
        ]

    def test_base_chain_order(self):
        assert [name for name, _ in self._scan_main().base_contracts()] == [
            "Base", "Ownable",
        ]

    def test_resolved_functions_include_inherited(self):
        names = {
            function.functionObject.node.name
            for function in self._scan_main().resolved_functions()
        }
        assert {"setValue", "setBase"} <= names

    def test_unknown_base_is_ignored(self, tmp_path):
        from ast_scanner.ast_scanner import Scanner
        from solidity_antlr4_parser.parser import objectify, parse_file

        (tmp_path / "a.sol").write_text(
            "pragma solidity ^0.8.0;\n"
            "contract A is MissingBase {\n"
            "    uint256 public a;\n"
            "}\n"
        )
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        tree = objectify(
            parse_file(str(tmp_path / "a.sol"), loc=True, strict=True),
            str(tmp_path / "a.sol"),
        )
        contract = Scanner(tree, project=project).contracts[0]
        assert contract.base_names == ["MissingBase"]
        assert contract.base_contracts() == []
        assert sorted(contract.resolved_state_vars()) == ["a"]

    def test_inheritance_cycle_terminates(self, tmp_path):
        from ast_scanner.ast_scanner import Scanner
        from solidity_antlr4_parser.parser import objectify, parse_file

        (tmp_path / "a.sol").write_text(
            "pragma solidity ^0.8.0;\n"
            'import "./b.sol";\n'
            "contract A is B {\n    uint256 public a;\n}\n"
        )
        (tmp_path / "b.sol").write_text(
            "pragma solidity ^0.8.0;\n"
            'import "./a.sol";\n'
            "contract B is A {\n    uint256 public b;\n}\n"
        )
        project = Project.load([tmp_path / "a.sol"], root=tmp_path)
        tree = objectify(
            parse_file(str(tmp_path / "a.sol"), loc=True, strict=True),
            str(tmp_path / "a.sol"),
        )
        contract = Scanner(tree, project=project).contracts[0]
        # must terminate and still expose both declarations
        assert sorted(contract.resolved_state_vars()) == ["a", "b"]
