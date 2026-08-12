"""Invocação de fase — spec: docs/specs/roteador-driver-invocacao.md (I1-I4)."""

from __future__ import annotations

from pathlib import Path

from invocacao import comando_de, invocar
from roteador import Fase


class ExecutorFalso:
    """Registra o que seria executado e devolve o que o teste mandar."""

    def __init__(self, exit_code: int = 0, saida: str = ""):
        self.exit_code = exit_code
        self.saida = saida
        self.chamadas: list[tuple[tuple[str, ...], Path]] = []

    def __call__(self, comando, cwd):
        self.chamadas.append((tuple(comando), Path(cwd)))
        return self.exit_code, self.saida


def test_cada_invocacao_e_um_processo(tmp_path: Path):
    # spec:I1
    executor = ExecutorFalso()
    invocar(Fase.CODIFICAR, "primeiro", alvo=tmp_path, executor=executor)
    invocar(Fase.CODIFICAR, "segundo", alvo=tmp_path, executor=executor)

    assert len(executor.chamadas) == 2
    assert executor.chamadas[0][0] != executor.chamadas[1][0]


def test_nenhuma_invocacao_retoma_sessao():
    # spec:I1 — retentativa é sessão nova; retomar traria o raciocínio anterior.
    comando = comando_de("qualquer prompt")
    for reuso in ("--resume", "--continue", "-c", "--session-id"):
        assert reuso not in comando


def test_o_executor_e_injetavel_e_a_suite_nao_chama_claude(tmp_path: Path):
    # spec:I2
    executor = ExecutorFalso()
    invocar(Fase.VERIFICAR, "prompt", alvo=tmp_path, executor=executor)
    assert executor.chamadas
    assert executor.chamadas[0][1] == tmp_path


def test_saida_e_registrada_e_nao_interpretada(tmp_path: Path):
    # spec:I3 — a fase pode dizer o que quiser; quem decide é exit code.
    executor = ExecutorFalso(exit_code=0, saida="FALHOU TUDO, nada foi feito")
    resultado = invocar(Fase.CODIFICAR, "p", alvo=tmp_path, executor=executor)

    assert resultado.saida == "FALHOU TUDO, nada foi feito"
    assert resultado.ok is True


def test_saida_otimista_nao_salva_exit_code_ruim(tmp_path: Path):
    # spec:I3
    executor = ExecutorFalso(exit_code=1, saida="tudo certo, 15 criterios atendidos")
    resultado = invocar(Fase.CODIFICAR, "p", alvo=tmp_path, executor=executor)
    assert resultado.ok is False


def test_exit_code_nao_zero_falha(tmp_path: Path):
    # spec:I4
    resultado = invocar(
        Fase.CODIFICAR, "p", alvo=tmp_path, executor=ExecutorFalso(exit_code=2)
    )
    assert resultado.ok is False
    assert resultado.exit_code == 2


def test_artefato_esperado_ausente_falha(tmp_path: Path):
    # spec:I4
    resultado = invocar(
        Fase.VERIFICAR,
        "p",
        alvo=tmp_path,
        artefato_esperado="docs/specs/alfa-veredito.md",
        executor=ExecutorFalso(exit_code=0),
    )
    assert resultado.artefato_presente is False
    assert resultado.ok is False


def test_artefato_esperado_presente_passa(tmp_path: Path):
    # spec:I4
    veredito = tmp_path / "docs" / "specs" / "alfa-veredito.md"
    veredito.parent.mkdir(parents=True)
    veredito.write_text("- **C1** — atendido\n", encoding="utf-8")

    resultado = invocar(
        Fase.VERIFICAR,
        "p",
        alvo=tmp_path,
        artefato_esperado="docs/specs/alfa-veredito.md",
        executor=ExecutorFalso(exit_code=0),
    )
    assert resultado.artefato_presente is True
    assert resultado.ok is True


def test_artefato_presente_nao_salva_exit_code_ruim(tmp_path: Path):
    # spec:I4 — as duas condições são conjuntivas; uma boa não compensa a outra.
    (tmp_path / "veredito.md").write_text("- **C1** — atendido\n", encoding="utf-8")

    resultado = invocar(
        Fase.VERIFICAR,
        "p",
        alvo=tmp_path,
        artefato_esperado="veredito.md",
        executor=ExecutorFalso(exit_code=1),
    )
    assert resultado.artefato_presente is True
    assert resultado.ok is False


def test_artefato_e_procurado_dentro_do_alvo(tmp_path: Path):
    # spec:I4 — caminho relativo ao alvo, nunca ao método.
    outro = tmp_path / "outro"
    outro.mkdir()
    (outro / "veredito.md").write_text("x", encoding="utf-8")

    resultado = invocar(
        Fase.VERIFICAR,
        "p",
        alvo=tmp_path / "alvo",
        artefato_esperado="veredito.md",
        executor=ExecutorFalso(exit_code=0),
    )
    assert resultado.ok is False
