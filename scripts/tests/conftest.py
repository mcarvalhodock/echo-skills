"""Fixtures pytest para os testes de instaladores.

Helpers e constantes ficam em ``_helpers.py`` — importar de lá para
evitar colisão de namespace com outros ``conftest.py`` do repositório.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


@pytest.fixture()
def fake_target(tmp_path: Path) -> Path:
    """Diretório temporário representando o repositório-alvo."""
    return tmp_path / "target"
