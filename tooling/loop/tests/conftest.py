"""Torna os módulos do loop importáveis pelos testes sem instalar pacote."""

from __future__ import annotations

import sys
from pathlib import Path

LOOP_ROOT = Path(__file__).resolve().parents[1]

if str(LOOP_ROOT) not in sys.path:
    sys.path.insert(0, str(LOOP_ROOT))
