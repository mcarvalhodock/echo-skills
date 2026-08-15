"""Carrega os scripts de CI como módulos, para os testes.

Separado de conftest.py para evitar colisão de namespace com outros
conftest.py do repositório (pytest unifica módulos com o mesmo nome).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

SCRIPTS_ROOT = Path(__file__).resolve().parents[1] / "scripts"


def _load(script_name: str, alias: str) -> ModuleType:
    script_path = SCRIPTS_ROOT / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(alias, script_path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"não foi possível carregar {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


criterion_coverage = _load("criterion_coverage", "sle_criterion_coverage")
pr_spec_diff = _load("pr_spec_diff", "sle_pr_spec_diff")
