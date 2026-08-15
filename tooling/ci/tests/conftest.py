"""Põe este diretório no path para que `_ci_helpers` seja importável.

O carregamento dos scripts mora em `_ci_helpers.py`, não aqui: módulos de
teste com o mesmo nome colidem quando a suíte completa roda de uma vez, e é
a suíte completa que `homologar` executa. Vale para `conftest.py` e vale
para o helper — daí o prefixo `_ci_`, e não `_helpers` genérico, que já
existe em `scripts/tests/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

TESTS_ROOT = Path(__file__).resolve().parent

if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))
