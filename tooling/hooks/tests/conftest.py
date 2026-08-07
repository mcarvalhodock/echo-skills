"""Fixtures compartilhadas e carregamento de hooks para testes do SLE.

Cada hook está em sua própria pasta como `hook.py`. Para evitar colisão de nomes
no `sys.modules`, carregamos cada um via `importlib` com um alias único e
exportamos como constantes ao nível do módulo. Testes importam esses aliases.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

HOOKS_ROOT = Path(__file__).resolve().parents[1]


def _load_hook(hook_dir_name: str, module_alias: str) -> ModuleType:
    hook_file = HOOKS_ROOT / hook_dir_name / "hook.py"
    spec = importlib.util.spec_from_file_location(module_alias, hook_file)
    if spec is None or spec.loader is None:  # pragma: no cover - defesa
        raise RuntimeError(f"não foi possível carregar hook em {hook_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_alias] = module
    spec.loader.exec_module(module)
    return module


designer_hook = _load_hook("block-designer-writing-code", "sle_designer_hook")


@pytest.fixture()
def project_root_with_manifest(tmp_path: Path) -> Path:
    """Repositório fake com .sle/manifesto.md contendo Paths de produção."""
    manifest_dir = tmp_path / ".sle"
    manifest_dir.mkdir()
    manifest = manifest_dir / "manifesto.md"
    manifest.write_text(
        "# Manifesto SLE\n\n"
        "## Paths de produção\n\n"
        "- `frontend/src/`\n"
        "- `backend/app/`\n\n"
        "## Domínios ativos\n\n"
        "- fundamentos\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def project_root_without_manifest(tmp_path: Path) -> Path:
    """Repositório fake sem manifesto — força uso de padrões default."""
    return tmp_path
