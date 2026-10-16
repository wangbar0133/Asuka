"""Cross-file project model.

Resolves import directives into a shared graph of parsed source units so
scanners can look up contracts, interfaces and libraries declared in
other files.

Import resolution is intentionally local-only:

- ``"./x.sol"`` / ``"../lib/x.sol"`` resolve relative to the importing file
- ``"/contracts/x.sol"`` resolves relative to the project root
- anything else (``"@openzeppelin/..."``, bare package paths) is treated
  as **external**: recorded but never resolved, because package layout
  conventions (node_modules, remappings) are out of scope.

A relative import that cannot be found is reported as **missing** - that
is a real error in the project, unlike an external dependency.

Imports are resolution-only: imported files are parsed and indexed, but
they are not scan targets (no findings are reported against a
dependency).
"""
from __future__ import annotations

from pathlib import Path

from solidity_antlr4_parser.parser import Node, objectify, parse_file

RESOLVED = "resolved"
EXTERNAL = "external"
MISSING = "missing"

CONTRACT_SOURCES = ("contracts", "libraries")


class ImportSpec:
    """One import directive of a source file."""

    def __init__(self, raw_path: str, node: Node, path: Path | None, kind: str):
        self.raw_path = raw_path   # as written in the source, quotes stripped
        self.node = node           # the ImportDirective AST node
        self.path = path           # absolute path when resolved, else None
        self.kind = kind           # RESOLVED | EXTERNAL | MISSING

    @property
    def is_resolved(self) -> bool:
        return self.kind == RESOLVED

    def __repr__(self) -> str:
        return f"ImportSpec({self.raw_path!r}, {self.kind})"


class SourceFile:
    """A parsed source file: objectified AST plus its import links."""

    def __init__(self, path: Path):
        self.path = path
        self.source_unit = None
        self.error: str | None = None
        self.imports: list[ImportSpec] = []

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def ok(self) -> bool:
        return self.source_unit is not None

    def symbol_names(self) -> list[str]:
        """Contract / interface / library names declared in this file."""
        if not self.ok:
            return []
        names: list[str] = []
        for attribute in CONTRACT_SOURCES:
            names += list(getattr(self.source_unit, attribute, {}).keys())
        return names

    def __repr__(self) -> str:
        if self.error:
            state = f"error={self.error!r}"
        elif self.ok:
            state = "ok"
        else:
            state = "unloaded"
        return f"SourceFile({self.name!r}, {state})"


class Project:
    """A graph of source files connected through local imports."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.files: dict[Path, SourceFile] = {}
        self.cycles: list[tuple[Path, Path]] = []
        self._symbols: dict[str, list[tuple[Path, object]]] | None = None

    # ------------------------------------------------------------------
    # loading
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, targets: list[str | Path], root: str | Path) -> Project:
        """Parse `targets` and transitively their local imports.

        Parse failures are recorded on the SourceFile (never raised), so
        a single broken dependency cannot abort loading.
        """
        project = cls(Path(root))
        for target in targets:
            project._load(Path(target).resolve(), ())
        return project

    def _load(self, path: Path, stack: tuple[Path, ...]) -> SourceFile:
        existing = self.files.get(path)
        if existing is not None:
            if path in stack:
                self.cycles.append((stack[-1], path))
            return existing

        source_file = SourceFile(path)
        # register before recursing so import cycles terminate
        self.files[path] = source_file

        try:
            tree = parse_file(str(path), loc=True, strict=True)
            source_file.source_unit = objectify(tree, str(path))
        except Exception as error:  # noqa: BLE001 - any parse failure is data
            source_file.error = f"{type(error).__name__}: {error}"
            return source_file

        for node in source_file.source_unit.imports:
            raw_path = (node.get("path") or "").strip().strip('"')
            resolved, kind = self.resolve_import(raw_path, path)
            source_file.imports.append(ImportSpec(raw_path, node, resolved, kind))
            if resolved is not None:
                self._load(resolved, stack + (path,))

        return source_file

    # ------------------------------------------------------------------
    # import resolution
    # ------------------------------------------------------------------
    def resolve_import(self, raw_path: str, importer: Path) -> tuple[Path | None, str]:
        """Resolve one import path written in `importer`.

        Returns (absolute path or None, kind).
        """
        if not raw_path:
            return None, MISSING

        if raw_path.startswith(("./", "../")):
            candidate = (importer.parent / raw_path).resolve()
            return (candidate, RESOLVED) if candidate.is_file() else (None, MISSING)

        if raw_path.startswith("/"):
            candidate = (self.root / raw_path.lstrip("/")).resolve()
            return (candidate, RESOLVED) if candidate.is_file() else (None, MISSING)

        # package-style path: try the project root as a convenience, but a
        # miss is an external dependency, not a broken project
        candidate = (self.root / raw_path).resolve()
        if candidate.is_file():
            return candidate, RESOLVED
        return None, EXTERNAL

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------
    @property
    def symbols(self) -> dict[str, list[tuple[Path, object]]]:
        """All declared symbols, name -> [(file, contractObject), ...]."""
        if self._symbols is None:
            symbols: dict[str, list[tuple[Path, object]]] = {}
            for path, source_file in self.files.items():
                if not source_file.ok:
                    continue
                for attribute in CONTRACT_SOURCES:
                    for name, contract in getattr(
                            source_file.source_unit, attribute, {}).items():
                        symbols.setdefault(name, []).append((path, contract))
            self._symbols = symbols
        return self._symbols

    def find_symbol(self, name: str) -> tuple[Path, object] | None:
        """First declaration of `name` (search order: load order)."""
        declarations = self.symbols.get(name)
        return declarations[0] if declarations else None

    def duplicate_symbols(self) -> dict[str, list[Path]]:
        """Symbol names declared in more than one file."""
        return {
            name: [path for path, _ in declarations]
            for name, declarations in self.symbols.items()
            if len(declarations) > 1
        }

    def missing_imports(self) -> list[tuple[Path, str]]:
        """(file, raw path) for every local import that cannot be found."""
        return [
            (source_file.path, spec.raw_path)
            for source_file in self.files.values()
            for spec in source_file.imports
            if spec.kind == MISSING
        ]

    def external_imports(self) -> list[tuple[Path, str]]:
        """(file, raw path) for every package-style import (not resolved)."""
        return [
            (source_file.path, spec.raw_path)
            for source_file in self.files.values()
            for spec in source_file.imports
            if spec.kind == EXTERNAL
        ]

    def failed_files(self) -> list[SourceFile]:
        return [source_file for source_file in self.files.values() if not source_file.ok]

    def imported_files(self, target: str | Path) -> list[Path]:
        """Transitive local imports of one target file (cycle-safe)."""
        start = Path(target).resolve()
        seen: set[Path] = set()
        queue = [start]
        while queue:
            current = queue.pop()
            source_file = self.files.get(current)
            if source_file is None:
                continue
            for spec in source_file.imports:
                if spec.path is not None and spec.path not in seen:
                    seen.add(spec.path)
                    queue.append(spec.path)
        seen.discard(start)
        return sorted(seen)

    def __repr__(self) -> str:
        return (
            f"Project(root={self.root.name!r}, files={len(self.files)}, "
            f"symbols={len(self.symbols)})"
        )


_PROJECT_CACHE: dict[tuple[str, tuple[str, ...]], Project] = {}


def project_for(root: str | Path, targets: list[str | Path]) -> Project:
    """Load (and memoise) the project for a scan root and its targets.

    The cache is process-local on purpose: multiprocessing workers each
    build the graph once on first use instead of receiving every parsed
    AST through pickling for every task.
    """
    key = (
        str(Path(root).resolve()),
        tuple(sorted(str(Path(target).resolve()) for target in targets)),
    )
    project = _PROJECT_CACHE.get(key)
    if project is None:
        project = Project.load(targets, root)
        _PROJECT_CACHE[key] = project
    return project


def clear_project_cache() -> None:
    """Drop the process-local project cache (used by tests)."""
    _PROJECT_CACHE.clear()
