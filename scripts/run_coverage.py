"""Executa a suíte de testes unitários e de integração medindo a cobertura de linhas (line coverage) via trace."""

from __future__ import annotations

import ast
import sys
import trace
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def executable_lines(py_file: Path) -> set[int]:
    """Determina as linhas executáveis de um módulo Python via AST (excluindo docstrings e definições puras)."""
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))
    lines: set[int] = set()

    for node in ast.walk(tree):
        # Ignora docstrings (Expr contendo Constant string)
        if isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            if isinstance(node.value.value, str):
                continue
        if isinstance(
            node,
            (
                ast.Assign,
                ast.AnnAssign,
                ast.AugAssign,
                ast.Return,
                ast.Raise,
                ast.Assert,
                ast.If,
                ast.For,
                ast.While,
                ast.With,
                ast.Try,
                ast.Import,
                ast.ImportFrom,
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Expr,
            ),
        ):
            lineno = getattr(node, "lineno", None)
            if lineno is not None:
                lines.add(lineno)
    return lines


def main() -> int:
    tracer = trace.Trace(count=1, trace=0)

    def run_suite() -> unittest.result.TestResult:
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=str(ROOT_DIR / "tests"), pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        return runner.run(suite)

    result: unittest.result.TestResult = tracer.runfunc(run_suite)
    if not result.wasSuccessful():
        print("\n[FAIL] A suíte de testes reportou falhas.", file=sys.stderr)
        return 1

    results = tracer.results()
    counts = results.counts

    pkg_dir = SRC_DIR / "agrocount"
    py_files = sorted(pkg_dir.glob("*.py"))

    total_exec = 0
    total_hit = 0
    print("\n=== Relatório de Cobertura de Linhas (u1-agrocount-platform) ===")
    print(f"{'Módulo':<35} {'Executadas':>12} {'Total':>10} {'Cobertura':>12}")
    print("-" * 73)

    for pf in py_files:
        resolved = str(pf.resolve())
        exec_set = executable_lines(pf)
        hit_set = {
            lineno
            for (filename, lineno), cnt in counts.items()
            if cnt > 0 and str(Path(filename).resolve()) == resolved and lineno in exec_set
        }
        mod_total = len(exec_set)
        mod_hit = len(hit_set)
        pct = (mod_hit / mod_total * 100.0) if mod_total > 0 else 100.0
        total_exec += mod_total
        total_hit += mod_hit
        print(f"{pf.relative_to(ROOT_DIR).as_posix():<35} {mod_hit:>12} {mod_total:>10} {pct:>11.1f}%")

    print("-" * 73)
    overall_pct = (total_hit / total_exec * 100.0) if total_exec > 0 else 100.0
    print(f"{'TOTAL (src/agrocount/)':<35} {total_hit:>12} {total_exec:>10} {overall_pct:>11.1f}%")

    if overall_pct < 80.0:
        print(f"\n[FAIL] Cobertura de linhas ({overall_pct:.1f}%) abaixo do piso mínimo de 80.0%.", file=sys.stderr)
        return 1

    print(f"\n[OK] Todos os testes passaram e a cobertura ({overall_pct:.1f}%) supera o piso de 80.0%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
