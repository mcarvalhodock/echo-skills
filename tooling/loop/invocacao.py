"""Executa uma fase num processo novo e devolve um resultado de máquina.

A regra que dá forma ao módulo: **o texto de retorno da fase nunca decide
nada.** Ele é guardado e mais nada. Duas rodadas seguidas de leitura limpa
escreveram o veredito no arquivo, como mandado, e devolveram um resumo dele no
canal de retorno — a regra "ninguém resume o veredito" foi cumprida no disco e
furada no retorno. Aqui o que decide é exit code e existência de artefato.

Impuro por definição: chama processo.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from roteador import Fase

MARCADOR = "{prompt}"

# O único comando verificado neste repositório. Outros agentes entram por
# configuração: chutar a flag de um executável que não está instalado aqui
# seria documentar algo que não funciona.
COMANDO_PADRAO = ("claude", "-p", MARCADOR)

# `especificar` é conversa: o agente pergunta e aprofunda a demanda, e é isso
# que faz a spec valer. Sem `-p`, o prompt semeia a primeira mensagem e o resto
# acontece entre você e ele.
COMANDO_INTERATIVO_PADRAO = ("claude", MARCADOR)


@dataclass(frozen=True)
class Resultado:
    fase: Fase
    exit_code: int
    saida: str
    artefato_esperado: str | None
    artefato_presente: bool

    @property
    def ok(self) -> bool:
        if self.exit_code != 0:
            return False
        return self.artefato_esperado is None or self.artefato_presente


def comando_de(prompt: str, template=COMANDO_PADRAO) -> tuple[str, ...]:
    """Headless, uma fase por processo, sem nenhuma retomada de sessão.

    Retomar sessão traria o raciocínio da fase anterior junto — que é
    exatamente o que a sessão limpa existe para cortar, e o motivo de
    retentativa também começar do zero.

    A posição do prompt é declarada pelo marcador, não presumida no fim: há
    agente que exige o texto antes das outras flags.
    """
    return tuple(arg.replace(MARCADOR, prompt) for arg in template)


def marcador_ausente(template) -> bool:
    """Erro de configuração deve doer antes da primeira invocação, não depois."""
    return not any(MARCADOR in arg for arg in template)


def executavel_ausente(template) -> str | None:
    """O nome do executável que não está no PATH, ou None."""
    if not template:
        return None
    return None if shutil.which(template[0]) else template[0]


def executar_de_verdade(comando, cwd) -> tuple[int, str]:
    concluido = subprocess.run(
        list(comando), cwd=str(cwd), capture_output=True, text=True
    )
    return concluido.returncode, (concluido.stdout or "") + (concluido.stderr or "")


def executar_interativo(comando, cwd) -> tuple[int, str]:
    """Sem capturar nada: o terminal é da conversa, não do driver.

    Interativo aqui não é flag do agente — é o driver saindo do meio. Capturar
    a saída roubaria o terminal de quem precisa responder às perguntas.
    """
    concluido = subprocess.run(list(comando), cwd=str(cwd))
    # Nada foi lido, e a string vazia diz isso. Fingir que há saída seria pior.
    return concluido.returncode, ""


def invocar(
    fase: Fase,
    prompt: str,
    *,
    alvo: Path | str,
    artefato_esperado: str | None = None,
    executor=None,
    template=COMANDO_PADRAO,
    interativo: bool = False,
) -> Resultado:
    executar = executor or (executar_interativo if interativo else executar_de_verdade)
    exit_code, saida = executar(comando_de(prompt, template), Path(alvo))

    presente = bool(artefato_esperado) and (Path(alvo) / artefato_esperado).exists()

    return Resultado(
        fase=fase,
        exit_code=exit_code,
        saida=saida,
        artefato_esperado=artefato_esperado,
        artefato_presente=presente,
    )
