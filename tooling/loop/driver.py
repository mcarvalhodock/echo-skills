"""O laço: percorre o lote invocando cada fase em sessão limpa.

Compõe as três peças já fechadas — `roteador.decidir`, `lote.decidir_lote` e a
invocação — sem reimplementar regra nenhuma delas. É a única camada que decide
**e** toca o mundo: lê arquivo, chama processo, carimba o instante e commita.

Duas coisas que o laço garante e que nenhuma das peças poderia garantir
sozinha: a decisão vai para o registro **antes** da invocação que ela ordena
(interromper e reexecutar não repete tentativa já contada), e o ref base de uma
spec é capturado uma vez, antes da primeira tentativa — retentativa não
reencurta o diff.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

import git_alvo
import invocacao
import registro
import skills_instaladas
from invocacao import COMANDO_PADRAO, invocar
from lote import (
    DecisaoDoLote,
    EstadoDoLote,
    SpecDoLote,
    decidir_lote,
    primeira_pendente,
    quarentena_de,
    spec_do_lote,
)
from roteador import TETO_PADRAO, Acao, Decisao, Fase, Motivo

FUSIVEL_PADRAO = 30

# O clone do método é onde este arquivo mora — não é configuração.
CLONE_DO_METODO = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    alvo: Path
    specs: tuple[str, ...]
    seco: bool = False
    fusivel: int = FUSIVEL_PADRAO
    teto: int = TETO_PADRAO
    comando: tuple[str, ...] = COMANDO_PADRAO


@dataclass(frozen=True)
class Relato:
    final: DecisaoDoLote
    invocacoes: int
    texto: str


def caminho_da_spec(alvo: Path | str, nome: str) -> Path:
    return Path(alvo) / "docs" / "specs" / f"{nome}.md"


def caminho_do_veredito(alvo: Path | str, nome: str) -> Path:
    return Path(alvo) / "docs" / "specs" / f"{nome}-veredito.md"


def montar_specs(alvo: Path | str, nomes) -> tuple[SpecDoLote, ...]:
    return tuple(
        spec_do_lote(nome, caminho_da_spec(alvo, nome).read_text(encoding="utf-8"))
        for nome in nomes
    )


def prompt_de(
    fase: Fase,
    *,
    alvo: Path,
    spec: str,
    base: str | None = None,
    escopo: str = ".",
) -> str:
    relativo = f"docs/specs/{spec}.md"
    if fase is Fase.CODIFICAR:
        return f"Use a skill codificar. Spec: {relativo}. Alvo: {alvo}."
    if fase is Fase.VERIFICAR:
        if base is None:
            # Sem git não há diff. A leitura limpa julga o estado atual — o que
            # ainda responde ao critério, porque critério é asserção sobre o
            # fim, não sobre o que mudou. O que se perde está declarado na spec.
            return (
                f"Use a skill verificar. Spec: {relativo}. "
                f"Sem git no alvo: leia o estado atual de {escopo} "
                f"(relativo ao alvo). Alvo: {alvo}."
            )
        # O escopo é relativo à RAIZ do repositório e o alvo já é a subárvore;
        # sem dizer isso, quem lê o prompt não sabe contra qual dos dois
        # resolver o caminho, e num monorepo os dois existem.
        return (
            f"Use a skill verificar. Spec: {relativo}. "
            f"Ref base do diff: {base}, limitado a {escopo} "
            f"(relativo à raiz do repositório). Alvo: {alvo}."
        )
    return f"Use a skill homologar. Alvo: {alvo}."


def rodar(config: Config, *, executor, agora=None, registrar=None) -> Relato:
    alvo = Path(config.alvo)
    carimbar = agora or _agora_iso
    gravar = registrar or registro.registrar

    if not alvo.is_dir():
        travado = _decisao_solta(Motivo.GUARDA_DO_ALVO, (f"alvo não existe: {alvo}",))
        return Relato(travado, 0, _texto_da_escalada(travado, alvo))

    if invocacao.marcador_ausente(config.comando):
        travado = _decisao_solta(
            Motivo.GUARDA_DO_ALVO,
            (f"comando sem o marcador {invocacao.MARCADOR}: {' '.join(config.comando)}",),
        )
        return Relato(travado, 0, _texto_da_escalada(travado, alvo))

    # Só quando o processo vai mesmo nascer: com executor injetado, a camada de
    # processo foi substituída inteira e checar o PATH não diz nada.
    if executor is None and (faltando := invocacao.executavel_ausente(config.comando)):
        travado = _decisao_solta(
            Motivo.GUARDA_DO_ALVO, (f"executável não encontrado no PATH: {faltando}",)
        )
        return Relato(travado, 0, _texto_da_escalada(travado, alvo))

    raiz_do_repo = git_alvo.raiz(alvo)
    com_git = raiz_do_repo is not None
    escopo = git_alvo.subarvore(alvo, raiz_do_repo) if com_git else "."
    avisos: list[str] = []

    if com_git:
        impedimentos = git_alvo.impedimentos(alvo)
        if impedimentos:
            travado = _decisao_solta(Motivo.GUARDA_DO_ALVO, tuple(impedimentos))
            return Relato(travado, 0, _texto_da_escalada(travado, alvo))
    else:
        # Uma vez, na abertura. Avisar a cada fase treina a pessoa a ignorar.
        avisos.append(
            "modo degradado: o alvo não é repositório git — sem commit por "
            "tentativa e sem diff na leitura limpa"
        )

    # A skill que o agente resolve é a instalada, não a do clone. Já rodou um
    # ciclo inteiro com uma versão anterior sem ninguém perceber.
    avisos.extend(skills_instaladas.divergencias(alvo, metodo=CLONE_DO_METODO))

    specs = montar_specs(alvo, config.specs)
    caminho_reg = registro.caminho_do_registro(alvo)
    if not config.seco:
        # Ciclo anterior que chegou ao fim vira arquivo; interrompido continua
        # aberto. É isso que impede uma spec emendada de nascer com o teto
        # esgotado pelas tentativas de semanas atrás.
        registro.arquivar_se_encerrado(caminho_reg)

    decisao = _abertura(specs)
    invocacoes = 0
    ultima_spec = decisao.proxima_spec or ""

    while decisao.decisao.acao is Acao.INVOCAR:
        fase = decisao.decisao.fase
        if fase is Fase.HOMOLOGAR:
            # Fim do lote. `homologar` termina num gate humano de qualquer
            # forma, e rodá-la sozinha produziria um checklist que ninguém
            # leria na hora em que foi gerado.
            break
        if config.seco:
            # Com os avisos: o ensaio também é "antes de começar", e é nele que
            # você tem chance de reinstalar a skill antes de rodar de verdade.
            texto = "\n".join([*avisos, _texto_seco(decisao, alvo, config)])
            return Relato(decisao, 0, texto)
        if invocacoes >= config.fusivel:
            decisao = _decisao_solta(Motivo.FUSIVEL, (f"{invocacoes} invocações",))
            break

        spec = decisao.proxima_spec
        ultima_spec = spec
        base = _base_registrada(caminho_reg, spec) if com_git else None
        if com_git and fase is Fase.CODIFICAR and base is None:
            base = git_alvo.head(alvo)

        gravar(
            caminho_reg,
            decisao=_com_base(decisao.decisao, fase, base, _base_registrada(caminho_reg, spec)),
            instante=carimbar(),
            alvo=alvo,
            spec=spec,
        )

        resultado = invocar(
            fase,
            prompt_de(fase, alvo=alvo, spec=spec, base=base, escopo=escopo),
            alvo=alvo,
            artefato_esperado=(
                f"docs/specs/{spec}-veredito.md" if fase is Fase.VERIFICAR else None
            ),
            executor=executor,
            template=config.comando,
        )
        invocacoes += 1

        if not resultado.ok:
            decisao = _decisao_solta(
                Motivo.FALHA_DE_INVOCACAO,
                (f"{fase.value} saiu com {resultado.exit_code}", spec),
                proxima=spec,
            )
            break

        if com_git and fase is Fase.CODIFICAR:
            git_alvo.commitar_tentativa(
                alvo, spec=spec, tentativa=registro.contar_tentativas(caminho_reg, spec)
            )

        specs = tuple(
            replace(s, fechada=s.fechada or s.nome in decisao.fechadas) for s in specs
        )
        decisao = decidir_lote(
            EstadoDoLote(
                specs=specs,
                fase_concluida=fase,
                spec_atual=spec,
                veredito=_veredito_de(alvo, spec) if fase is Fase.VERIFICAR else None,
                tentativas=registro.contar_tentativas(caminho_reg, spec),
                teto=config.teto,
                vereditos=(str(caminho_do_veredito(alvo, spec)),),
            )
        )

    # A decisão que encerra também vai para o registro. Sem ela o arquivo só
    # tem invocações e não sabe dizer por que o loop parou — e é ela que a
    # execução seguinte lê para saber se retoma ou começa ciclo novo.
    #
    # Sob `seco`, não. O laço pode terminar antes da primeira iteração — lote
    # todo em quarentena, ou nada pendente — e aí a saída seca nunca é
    # alcançada; sem esta guarda, um ensaio escreveria no alvo.
    if not config.seco:
        gravar(
            caminho_reg,
            decisao=decisao.decisao,
            instante=carimbar(),
            alvo=alvo,
            spec=ultima_spec,
        )

    texto = (
        _texto_do_fechamento(decisao)
        if decisao.decisao.acao is Acao.INVOCAR
        else _texto_da_escalada(decisao, alvo)
    )
    return Relato(decisao, invocacoes, "\n".join([*avisos, texto]))


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _abertura(specs: tuple[SpecDoLote, ...]) -> DecisaoDoLote:
    quarentena = quarentena_de(specs)
    fechadas = tuple(s.nome for s in specs if s.fechada)
    insumos = tuple(
        (
            s.nome,
            s.insumo_faltante
            or tuple(n for n in s.depende_de if n in quarentena),
        )
        for s in specs
        if s.nome in quarentena
    )
    ordenada = tuple(s.nome for s in specs if s.nome in quarentena)
    primeira = primeira_pendente(specs)

    if primeira is None:
        decisao = (
            Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.HOMOLOGAR)
            if fechadas
            else Decisao(Acao.ESCALAR, Motivo.LOTE_VAZIO, evidencia=ordenada)
        )
        return DecisaoDoLote(decisao, None, fechadas, ordenada, insumos)

    return DecisaoDoLote(
        Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.CODIFICAR),
        primeira,
        fechadas,
        ordenada,
        insumos,
    )


def _decisao_solta(motivo: Motivo, evidencia, proxima=None) -> DecisaoDoLote:
    return DecisaoDoLote(Decisao(Acao.ESCALAR, motivo, evidencia=tuple(evidencia)), proxima)


def _com_base(decisao: Decisao, fase: Fase, base, ja_registrada) -> Decisao:
    """O ref base viaja na evidência da PRIMEIRA invocação de codificar.

    O registro tem esquema fechado e não ganha campo por isto; a evidência de
    uma decisão que ainda não tem critério reprovado estava livre, e é a única
    linha da spec cujo lugar no tempo é exatamente "antes da primeira tentativa".
    """
    if fase is Fase.CODIFICAR and ja_registrada is None and base:
        return replace(decisao, evidencia=(base,))
    return decisao


def _base_registrada(caminho_reg, spec: str) -> str | None:
    for linha in registro.linhas(caminho_reg):
        if linha.get("spec") == spec and linha.get("transicao") == "invocar:codificar":
            evidencia = linha.get("evidencia") or []
            return evidencia[0] if evidencia else None
    return None


def _veredito_de(alvo: Path, spec: str) -> str | None:
    caminho = caminho_do_veredito(alvo, spec)
    return caminho.read_text(encoding="utf-8") if caminho.exists() else None


def _texto_da_escalada(decisao: DecisaoDoLote, alvo: Path) -> str:
    d = decisao.decisao
    linhas = [
        f"parou: {d.motivo.value}",
        f"spec: {decisao.proxima_spec or '—'}",
        f"evidência: {', '.join(d.evidencia) if d.evidencia else '—'}",
    ]
    if decisao.proxima_spec:
        # Caminhos, nunca conteúdo: o veredito audita a sessão que o pediu, e
        # transcrevê-lo aqui é a forma de amaciá-lo sem má intenção.
        linhas.append(f"spec em: {caminho_da_spec(alvo, decisao.proxima_spec)}")
        linhas.append(f"veredito em: {caminho_do_veredito(alvo, decisao.proxima_spec)}")
    linhas.append(f"registro em: {registro.caminho_do_registro(alvo)}")
    return "\n".join(linhas)


def _texto_do_fechamento(decisao: DecisaoDoLote) -> str:
    linhas = [
        "lote encerrado",
        f"fechadas: {', '.join(decisao.fechadas) or '—'}",
        f"quarentena: {', '.join(decisao.quarentena) or '—'}",
    ]
    for nome, insumos in decisao.insumos_faltantes:
        linhas.append(f"  {nome} espera: {', '.join(insumos) or '—'}")
    return "\n".join(linhas)


def _texto_seco(decisao: DecisaoDoLote, alvo: Path, config: Config) -> str:
    d = decisao.decisao
    fase = d.fase.value if d.fase else d.motivo.value
    return "\n".join(
        [
            "modo seco — nada foi invocado, registrado ou commitado",
            f"próxima decisão: {d.acao.value}:{fase}",
            f"spec: {decisao.proxima_spec or '—'}",
            f"insumos: spec={caminho_da_spec(alvo, decisao.proxima_spec)} "
            f"alvo={alvo} teto={config.teto} fusível={config.fusivel}",
        ]
    )


def main(argv=None) -> int:
    analisador = argparse.ArgumentParser(
        description=(
            "Loop SLE — percorre um lote de specs já aprovadas, invocando cada "
            "fase em sessão limpa. Para nos gates humanos e nas exceções."
        ),
        epilog=(
            "Exemplo:\n"
            "  python tooling/loop/driver.py --alvo ../meu-projeto "
            "--specs cadastro,cobranca --seco\n\n"
            "O alvo precisa estar limpo e fora do branch default."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analisador.add_argument(
        "--alvo", required=True, help="caminho do codebase sobre o qual rodar"
    )
    analisador.add_argument(
        "--specs",
        required=True,
        help="nomes separados por vírgula, sem caminho e sem .md "
        "(lidos de <alvo>/docs/specs/<nome>.md)",
    )
    analisador.add_argument(
        "--seco",
        action="store_true",
        help="mostra a próxima decisão e para: não invoca, não registra, não commita",
    )
    analisador.add_argument(
        "--fusivel",
        type=int,
        default=FUSIVEL_PADRAO,
        help=f"máximo de invocações no ciclo inteiro (default: {FUSIVEL_PADRAO})",
    )
    analisador.add_argument(
        "--teto",
        type=int,
        default=TETO_PADRAO,
        help=f"máximo de tentativas de codificar por spec (default: {TETO_PADRAO})",
    )
    analisador.add_argument(
        "--comando",
        default=" ".join(COMANDO_PADRAO),
        help="como invocar o agente; %s marca onde entra o texto "
        "(default: %s). Ex.: 'agent -p %s'"
        % (invocacao.MARCADOR, " ".join(COMANDO_PADRAO), invocacao.MARCADOR),
    )
    args = analisador.parse_args(argv)

    config = Config(
        alvo=Path(args.alvo),
        specs=tuple(nome.strip() for nome in args.specs.split(",") if nome.strip()),
        seco=args.seco,
        fusivel=args.fusivel,
        teto=args.teto,
        comando=tuple(args.comando.split()),
    )
    relato = rodar(config, executor=None)
    print(relato.texto)
    return 0 if relato.final.decisao.acao is Acao.INVOCAR else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
