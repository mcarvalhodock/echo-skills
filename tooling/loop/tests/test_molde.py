"""O molde tem um dono só — spec: docs/specs/loop-auditoria.md (F7)."""

from __future__ import annotations

from pathlib import Path

import auditoria
import driver
import molde

SKILL_VERIFICAR = driver.CLONE_DO_METODO / "verificar" / "SKILL.md"


def _texto_da_skill() -> str:
    return SKILL_VERIFICAR.read_text(encoding="utf-8")


def test_as_linhas_invariantes_vieram_da_skill():
    # spec:F7 — se alguém reescrever o molde na skill sem tocar no código, ou
    # o contrário, isto reprova. É o que impede as duas cópias divergirem.
    texto = _texto_da_skill()

    assert molde.CLASSIFICACAO in texto, "a linha de classificação divergiu da skill"
    assert molde.LIMITE in texto, "a linha de limite divergiu da skill"


def test_a_variante_sem_diff_e_a_mesma_da_skill():
    # spec:F7 — a primeira linha, com os marcadores da skill em vez de valores.
    montado = molde.contra_estado_atual(
        spec="<alvo>/docs/specs/<nome>.md",
        escopo="<escopo>",
        saida="<alvo>/docs/specs/<nome>-veredito.md",
    )
    primeira = montado.splitlines()[0]

    assert primeira in _texto_da_skill(), (
        f"a variante sem diff divergiu da skill: {primeira!r}"
    )


def test_a_auditoria_usa_o_molde_e_nao_um_literal_proprio(monkeypatch):
    # spec:F7 — trocar o dono do molde muda o que a auditoria emite.
    monkeypatch.setattr(
        molde, "contra_estado_atual", lambda **k: "MOLDE-SUBSTITUIDO"
    )

    assert auditoria.prompt_de(Path("/alvo"), "alfa") == "MOLDE-SUBSTITUIDO"


def test_o_prompt_da_auditoria_nao_cita_skill_nem_git():
    # spec:F7 — reusar `driver.prompt_de(VERIFICAR)` traria as duas coisas, e
    # as duas seriam falsas aqui.
    prompt = auditoria.prompt_de(Path("/alvo"), "alfa", escopo=".")

    assert "Use a skill" not in prompt
    assert "Sem git" not in prompt
    assert "alfa-auditoria.md" in prompt
