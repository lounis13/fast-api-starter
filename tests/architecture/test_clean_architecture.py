from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


def _iter_python_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.py"):
        # Skip __init__.py files if desired, but they can be included safely
        yield p


def _package_of_file(py_file: Path) -> str:
    # Convert path like app/domain/services.py -> app.domain
    rel = py_file.relative_to(PROJECT_ROOT).with_suffix("")
    parts = list(rel.parts)
    # remove the module filename to keep only the package path
    if parts and parts[-1] != "__init__":
        parts = parts[:-1]
    # if file is app/__init__.py, parts == ["app"]
    return ".".join(parts)


def _resolve_absolute_from(module_pkg: str, node: ast.ImportFrom, alias: str | None = None) -> str | None:
    """
    Resolve an absolute module path from an ImportFrom node, handling relative imports.
    If alias is provided and node.module is None (e.g., from .. import infrastructure),
    it will be appended as the last segment.
    """
    level = getattr(node, "level", 0) or 0
    base_parts = module_pkg.split(".") if module_pkg else []

    # Walk up 'level' parents (level=0 means absolute import)
    if level > 0:
        if len(base_parts) >= level:
            base_parts = base_parts[: len(base_parts) - level]
        else:
            base_parts = []

    module = node.module
    parts: List[str] = []
    if base_parts:
        parts.extend(base_parts)
    if module:
        parts.extend(module.split("."))
    elif alias:
        parts.append(alias)

    if not parts:
        return None
    return ".".join(parts)


def _collect_imports(py_file: Path) -> List[Tuple[str, int, str]]:
    """
    Return list of tuples: (kind, lineno, module), where kind in {"import", "from"}
    and module is the absolute (best-effort) module path or the raw name for direct imports.
    """
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))
    file_pkg = _package_of_file(py_file)

    results: List[Tuple[str, int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append(("import", node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module is None:
                # from .. import something
                for alias in node.names:
                    abs_mod = _resolve_absolute_from(file_pkg, node, alias=alias.name)
                    if abs_mod:
                        results.append(("from", node.lineno, abs_mod))
            else:
                abs_mod = _resolve_absolute_from(file_pkg, node)
                if abs_mod:
                    results.append(("from", node.lineno, abs_mod))

    return results


def _assert_no_forbidden_imports(root: Path, forbidden_prefixes: List[str], *, label: str) -> None:
    violations: List[str] = []
    for file in _iter_python_files(root):
        imports = _collect_imports(file)
        for kind, lineno, module in imports:
            for prefix in forbidden_prefixes:
                if module == prefix or module.startswith(prefix + "."):
                    rel = file.relative_to(PROJECT_ROOT)
                    violations.append(f"{rel}:{lineno} -> {kind} {module}")
                    break
    if violations:
        joined = "\n".join(violations)
        raise AssertionError(
            f"Architecture rule violated for {label}: forbidden imports detected (prefixes: {forbidden_prefixes})\n{joined}"
        )


def test_domain_does_not_depend_on_infrastructure_or_api():
    domain_root = APP_ROOT / "domain"
    assert domain_root.exists(), "Expected app/domain to exist"
    forbidden = [
        "app.infrastructure",
        "app.api",
        "app.di",
    ]
    _assert_no_forbidden_imports(domain_root, forbidden, label="domain")


def test_application_does_not_depend_on_infrastructure_or_api():
    application_root = APP_ROOT / "application"
    assert application_root.exists(), "Expected app/application to exist"
    forbidden = [
        "app.infrastructure",
        "app.api",
    ]
    _assert_no_forbidden_imports(application_root, forbidden, label="application")


def _assert_no_external_frameworks(root: Path, banned_modules: List[str], *, label: str) -> None:
    violations: List[str] = []
    for file in _iter_python_files(root):
        imports = _collect_imports(file)
        for kind, lineno, module in imports:
            for banned in banned_modules:
                if module == banned or module.startswith(banned + "."):
                    rel = file.relative_to(PROJECT_ROOT)
                    violations.append(f"{rel}:{lineno} -> {kind} {module}")
                    break
    if violations:
        joined = "\n".join(violations)
        raise AssertionError(
            f"Clean code rule violated for {label}: infrastructure/web frameworks used in {label}\n{joined}"
        )


def test_domain_does_not_use_web_or_io_frameworks():
    domain_root = APP_ROOT / "domain"
    banned = [
        "fastapi",
        "httpx",
        "uvicorn",
    ]
    _assert_no_external_frameworks(domain_root, banned, label="domain")


def test_application_does_not_use_web_or_io_frameworks():
    application_root = APP_ROOT / "application"
    banned = [
        "fastapi",
        "httpx",
        "uvicorn",
    ]
    _assert_no_external_frameworks(application_root, banned, label="application")
