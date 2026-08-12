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

import auditoria
import casa
import git_alvo
import invocacao
import painel
import pedidos
import registro
import repos
import secoes
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

# O mesmo teto que `especificar` declara. O relatório do gate expõe quando ele
# foi furado, em vez de deixar passar num lote de seis specs.
TETO_DE_CRITERIOS = 15

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
    comando_interativo: tuple[str, ...] = invocacao.COMANDO_INTERATIVO_PADRAO
    pedidos: str | None = None


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
    pedido: str = "",
) -> str:
    relativo = f"docs/specs/{spec}.md"
    if fase is Fase.CODIFICAR:
        return f"Use a skill codificar. Spec: {relativo}. Alvo: {alvo}."
    if fase is Fase.ESPECIFICAR:
        return (
            f"Use a skill especificar. Nome da spec: {spec}. "
            f"Alvo: {alvo}.\n\nPedido:\n{pedido}"
        )
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
    return (
        f"Use a skill homologar. Specs do ciclo: {spec}. "
        f"Vereditos: {escopo}. Ref base do ciclo: {base}. Alvo: {alvo}."
    )


@dataclass(frozen=True)
class Contexto:
    alvo: Path
    com_git: bool
    escopo: str
    avisos: tuple[str, ...]


def _preparar(
    config: Config, executor, comando=None
) -> tuple[Contexto | None, Relato | None]:
    """As guardas que valem para os dois segmentos. Uma só, para não divergirem.

    `comando` é o do segmento que vai rodar: o segmento 1 usa o interativo, e
    validar o headless ali deixaria passar template interativo quebrado.
    """
    alvo = Path(config.alvo)
    comando = comando or config.comando

    def travar(*motivos: str) -> tuple[None, Relato]:
        decisao = _decisao_solta(Motivo.GUARDA_DO_ALVO, motivos)
        return None, Relato(decisao, 0, _texto_da_escalada(decisao, alvo))

    if not alvo.is_dir():
        return travar(f"alvo não existe: {alvo}")

    if invocacao.marcador_ausente(comando):
        return travar(
            f"comando sem o marcador {invocacao.MARCADOR}: {' '.join(comando)}"
        )

    # Só quando o processo vai mesmo nascer: com executor injetado, a camada de
    # processo foi substituída inteira e checar o PATH não diz nada.
    if executor is None and (faltando := invocacao.executavel_ausente(comando)):
        return travar(f"executável não encontrado no PATH: {faltando}")

    raiz_do_repo = git_alvo.raiz(alvo)
    com_git = raiz_do_repo is not None
    avisos: list[str] = []

    if com_git:
        if impedimentos := git_alvo.impedimentos(alvo):
            return travar(*impedimentos)
    else:
        # Uma vez, na abertura. Avisar a cada fase treina a pessoa a ignorar.
        avisos.append(
            "modo degradado: o alvo não é repositório git — sem commit por "
            "tentativa e sem diff na leitura limpa"
        )

    # A skill que o agente resolve é a instalada, não a do clone. Já rodou um
    # ciclo inteiro com uma versão anterior sem ninguém perceber.
    avisos.extend(skills_instaladas.divergencias(alvo, metodo=CLONE_DO_METODO))

    return (
        Contexto(
            alvo=alvo,
            com_git=com_git,
            escopo=git_alvo.subarvore(alvo, raiz_do_repo) if com_git else ".",
            avisos=tuple(avisos),
        ),
        None,
    )


def rodar(config: Config, *, executor, agora=None, registrar=None) -> Relato:
    carimbar = agora or _agora_iso
    gravar = registrar or registro.registrar

    contexto, travado = _preparar(config, executor)
    if travado is not None:
        return travado
    alvo, com_git, escopo = contexto.alvo, contexto.com_git, contexto.escopo
    avisos = list(contexto.avisos)

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

    saida_da_homologacao = ""
    auditado = False

    while decisao.decisao.acao is Acao.INVOCAR:
        fase = decisao.decisao.fase
        if config.seco:
            # Com os avisos: o ensaio também é "antes de começar", e é nele que
            # você tem chance de reinstalar a skill antes de rodar de verdade.
            texto = "\n".join([*avisos, _texto_seco(decisao, alvo, config)])
            return Relato(decisao, 0, texto)
        if invocacoes >= config.fusivel:
            decisao = _decisao_solta(Motivo.FUSIVEL, (f"{invocacoes} invocações",))
            break

        # `homologar` fecha o ciclo e não tem spec própria: os insumos dela são
        # o conjunto do ciclo e a base do começo dele, não da última demanda.
        fecha_o_ciclo = fase is Fase.HOMOLOGAR

        if fecha_o_ciclo and not auditado:
            # Antes do checklist, e não depois: pergunta de arquitetura sobre
            # código com critério regredido é pergunta prematura.
            regredidas, invocacoes = _auditar(
                alvo, escopo, config, executor, invocacoes
            )
            auditado = True
            if regredidas:
                decisao = _decisao_solta(
                    Motivo.REGRESSAO_DE_CRITERIO, tuple(sorted(regredidas))
                )
                break
        spec = ", ".join(decisao.fechadas) if fecha_o_ciclo else decisao.proxima_spec
        if not fecha_o_ciclo:
            ultima_spec = spec

        base = _base_registrada(caminho_reg, spec) if com_git else None
        if fecha_o_ciclo:
            base = _base_do_ciclo(caminho_reg) if com_git else None
        elif com_git and fase is Fase.CODIFICAR and base is None:
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
            prompt_de(
                fase,
                alvo=alvo,
                spec=spec,
                base=base,
                escopo=(
                    ", ".join(
                        str(caminho_do_veredito(alvo, n)) for n in decisao.fechadas
                    )
                    if fecha_o_ciclo
                    else escopo
                ),
            ),
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

        if fecha_o_ciclo:
            # Repassada na íntegra, nunca resumida: o checklist é endereçado a
            # você e não tem arquivo próprio. Parafrasear é o que amacia um
            # parecer; encaminhar verbatim é o oposto disso.
            saida_da_homologacao = resultado.saida

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
                spec_atual=ultima_spec,
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
    partes = [*avisos]
    if saida_da_homologacao:
        # O ciclo fechou: as três listas continuam devidas (D10) mesmo agora que
        # a última parada é o checklist, e não mais o próprio `homologar`.
        partes.extend([_texto_do_fechamento(decisao), texto, saida_da_homologacao])
    else:
        partes.append(texto)
    return Relato(decisao, invocacoes, "\n".join(partes))


def rodar_pedidos(config: Config, *, executor, agora=None, registrar=None) -> Relato:
    """Segmento 1: escreve as specs e para no gate. Nunca chama `codificar`."""
    carimbar = agora or _agora_iso
    gravar = registrar or registro.registrar
    alvo = Path(config.alvo)

    if config.specs and config.pedidos:
        # A fronteira entre os dois segmentos é explícita de propósito: a
        # aprovação é o ato de rodar o segundo comando, não um campo na spec.
        return _travado(alvo, "--pedidos e --specs são exclusivos")

    contexto, travado = _preparar(config, executor, config.comando_interativo)
    if travado is not None:
        return travado
    alvo, com_git = contexto.alvo, contexto.com_git

    caminho = alvo / (config.pedidos or "pedidos.md")
    if not caminho.exists():
        return _travado(alvo, f"arquivo de pedidos não encontrado: {caminho}")

    leitura = pedidos.ler(caminho.read_text(encoding="utf-8"))
    if leitura.invalidos:
        return _travado(
            alvo,
            *(
                f"cabeçalho não serve como nome de spec: {titulo}"
                for titulo in leitura.invalidos
            ),
        )
    if not leitura.pedidos:
        return _travado(alvo, f"nenhum pedido em {caminho}")

    if config.seco:
        # `--seco` significa a mesma coisa nos dois segmentos: nada é invocado,
        # registrado ou commitado. Aqui isso seria N chamadas ao agente.
        fila = [
            f"  {p.nome}: {'pularia — a spec já existe' if caminho_da_spec(alvo, p.nome).exists() else 'especificaria'}"
            for p in leitura.pedidos
        ]
        parado = _decisao_solta(Motivo.GATE_SPEC_APROVADA, ())
        return Relato(
            parado,
            0,
            "\n".join(
                [
                    *contexto.avisos,
                    "modo seco — nada foi invocado, registrado ou commitado",
                    f"fila de {len(leitura.pedidos)} pedido(s) em {caminho}:",
                    *fila,
                ]
            ),
        )

    caminho_reg = registro.caminho_do_registro(alvo)
    registro.arquivar_se_encerrado(caminho_reg)
    if com_git:
        git_alvo.commitar_pedidos(alvo)

    linhas: list[str] = []
    invocacoes = 0

    for pedido in leitura.pedidos:
        if caminho_da_spec(alvo, pedido.nome).exists():
            # Reescrever spec sua a partir de um pedido antigo destruiria
            # trabalho já revisado. Pular e dizer é a única saída honesta.
            linhas.append(f"  {pedido.nome}: pulado — a spec já existe")
            continue

        if not config.seco:
            gravar(
                caminho_reg,
                decisao=Decisao(Acao.INVOCAR, Motivo.TRANSICAO, fase=Fase.ESPECIFICAR),
                instante=carimbar(),
                alvo=alvo,
                spec=pedido.nome,
            )

        resultado = invocar(
            Fase.ESPECIFICAR,
            prompt_de(
                Fase.ESPECIFICAR, alvo=alvo, spec=pedido.nome, pedido=pedido.texto
            ),
            alvo=alvo,
            artefato_esperado=f"docs/specs/{pedido.nome}.md",
            executor=executor,
            template=config.comando_interativo,
            interativo=True,
        )
        invocacoes += 1

        if not resultado.ok:
            final = _decisao_solta(
                Motivo.FALHA_DE_INVOCACAO,
                (f"especificar saiu com {resultado.exit_code}", pedido.nome),
                proxima=pedido.nome,
            )
            _gravar_final(gravar, caminho_reg, final, carimbar, alvo, pedido.nome, config)
            return Relato(
                final,
                invocacoes,
                "\n".join([*contexto.avisos, _texto_da_escalada(final, alvo)]),
            )

        if com_git:
            git_alvo.commitar_spec(alvo, spec=pedido.nome)
        linhas.append(_linha_do_relatorio(alvo, pedido.nome))

    final = _decisao_solta(Motivo.GATE_SPEC_APROVADA, ())
    _gravar_final(gravar, caminho_reg, final, carimbar, alvo, "", config)

    cabecalho = "lote de specs escrito — revise antes de rodar o segundo comando"
    return Relato(final, invocacoes, "\n".join([*contexto.avisos, cabecalho, *linhas]))


def _linha_do_relatorio(alvo: Path, nome: str) -> str:
    """Uma linha por spec, com o que se precisa para triar — não só listar."""
    texto = caminho_da_spec(alvo, nome).read_text(encoding="utf-8")
    criterios = secoes.criterios(texto)
    dominios = sorted({d for _, marcados in criterios for d in marcados})

    linha = f"  {nome}: {len(criterios)} critérios"
    if dominios:
        linha += f" [{', '.join(dominios)}]"
    if len(criterios) > TETO_DE_CRITERIOS:
        linha += f" — acima do teto de {TETO_DE_CRITERIOS}"

    perguntas = secoes.perguntas_em_aberto(texto)
    if perguntas:
        linha += f" — bloqueada: {'; '.join(perguntas)}"
    return linha


def _travado(alvo: Path, *motivos: str) -> Relato:
    decisao = _decisao_solta(Motivo.GUARDA_DO_ALVO, motivos)
    return Relato(decisao, 0, _texto_da_escalada(decisao, alvo))


def _gravar_final(gravar, caminho_reg, decisao, carimbar, alvo, spec, config) -> None:
    if not config.seco:
        gravar(
            caminho_reg,
            decisao=decisao.decisao,
            instante=carimbar(),
            alvo=alvo,
            spec=spec,
        )


def _comando_painel(args) -> int:
    """Relata, não julga: sai com 0 mesmo havendo travado."""
    if args.alvo:
        alvo = repos.resolver_cadastrado(args.alvo)
        print(painel.linha_de(args.alvo, alvo))
        return 0

    for repo in repos.carregar():
        print(painel.linha_de(repo.apelido, repo.caminho))
    return 0


def _comando_repo(args, analisador) -> int:
    """`repo` mexe só no cadastro: nenhum alvo é tocado por causa dele."""
    _, criada = casa.garantir()
    if criada:
        print(f"casa criada em {casa.caminho()}")

    # Linha que não serve é nomeada, sempre. Coletá-la e não mostrar seria pior
    # que não coletar: some em silêncio e a pessoa acha que cadastrou.
    for linha in repos.leitura_atual().invalidos:
        print(f"linha ignorada, fora do formato `- <apelido>: <caminho>`: {linha}")

    if args.acao == "list":
        for repo in repos.carregar():
            estado = "" if repos.existe(repo) else "  (ausente)"
            print(f"{repo.apelido}: {repo.caminho}{estado}")
        return 0

    try:
        if args.acao == "add":
            repos.gravar(
                repos.adicionar(repos.texto_atual(), args.apelido, args.caminho)
            )
        elif args.acao == "rm":
            repos.gravar(repos.remover(repos.texto_atual(), args.apelido))
        else:
            analisador.print_help()
            return 2
    except (repos.ApelidoEmUso, repos.ApelidoDesconhecido) as recusa:
        print(str(recusa))
        return 1
    return 0


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


def _auditar(alvo: Path, escopo: str, config: Config, executor, invocacoes: int):
    """Relê os critérios de todas as specs do alvo. Devolve as que regrediram.

    Uma invocação por spec, e cada uma conta no fusível: o custo é real e
    cresce com o alvo, e é o preço de não acreditar em veredito velho.
    """
    regredidas: list[str] = []

    for nome in auditoria.auditaveis(alvo):
        invocar(
            Fase.VERIFICAR,  # é leitura limpa; não há fase nova aqui
            auditoria.prompt_de(alvo, nome, escopo=escopo),
            alvo=alvo,
            artefato_esperado=f"docs/specs/{nome}-auditoria.md",
            executor=executor,
            template=config.comando,
        )
        invocacoes += 1
        if auditoria.regressoes(alvo, nome):
            regredidas.append(nome)

    return regredidas, invocacoes


def _base_do_ciclo(caminho_reg) -> str | None:
    """A base da PRIMEIRA spec do ciclo — a última já teria commits em cima."""
    for linha in registro.linhas(caminho_reg):
        if linha.get("transicao") == "invocar:codificar" and linha.get("evidencia"):
            return linha["evidencia"][0]
    return None


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
    if d.motivo is Motivo.REGRESSAO_DE_CRITERIO:
        # A evidência aqui são nomes de spec, e cada uma tem sua auditoria.
        for nome in d.evidencia:
            linhas.append(f"auditoria em: {auditoria.caminho_da_auditoria(alvo, nome)}")
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


GATES_PLANEJADOS = (Motivo.GATE_SPEC_APROVADA, Motivo.GATE_CHECKLIST)


def _comuns(sub) -> None:
    sub.add_argument("--alvo", required=True, help="caminho do codebase")
    sub.add_argument(
        "--seco",
        action="store_true",
        help="mostra o que faria e para: não invoca, não registra, não commita",
    )
    sub.add_argument(
        "--comando",
        default=" ".join(COMANDO_PADRAO),
        help="fases headless; %s marca onde entra o texto (default: %s)"
        % (invocacao.MARCADOR, " ".join(COMANDO_PADRAO)),
    )
    sub.add_argument(
        "--comando-interativo",
        default=" ".join(invocacao.COMANDO_INTERATIVO_PADRAO),
        help="a sessão de conversa de `pedir`; sem flag headless (default: %s)"
        % " ".join(invocacao.COMANDO_INTERATIVO_PADRAO),
    )


def main(argv=None) -> int:
    analisador = argparse.ArgumentParser(
        prog="sle",
        description=(
            "Loop SLE — `pedir` conversa e escreve as specs; `rodar` executa o "
            "lote headless até o checklist. Um gate humano entre os dois."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subcomandos = analisador.add_subparsers(dest="subcomando")

    pedir = subcomandos.add_parser(
        "pedir", help="segmento 1: uma sessão interativa por demanda de pedidos.md"
    )
    _comuns(pedir)
    pedir.add_argument(
        "--pedidos",
        default="pedidos.md",
        help="arquivo de pedidos, relativo ao alvo (default: pedidos.md)",
    )

    quadro = subcomandos.add_parser(
        "painel", help="o que cada repositório espera de você"
    )
    quadro.add_argument(
        "--alvo", default=None, help="mostra só este (apelido ou caminho)"
    )

    repo = subcomandos.add_parser("repo", help="cadastro de repositórios")
    acoes = repo.add_subparsers(dest="acao")
    adicionar = acoes.add_parser("add", help="registra um repositório")
    adicionar.add_argument("apelido")
    adicionar.add_argument("caminho")
    acoes.add_parser("list", help="lista os registrados")
    remover = acoes.add_parser("rm", help="remove um registrado")
    remover.add_argument("apelido")

    rodar_cmd = subcomandos.add_parser(
        "rodar", help="segmento 2: codificar/verificar por spec e homologar no fim"
    )
    _comuns(rodar_cmd)
    rodar_cmd.add_argument(
        "--specs",
        required=True,
        help="nomes separados por vírgula, sem caminho e sem .md",
    )
    rodar_cmd.add_argument(
        "--fusivel",
        type=int,
        default=FUSIVEL_PADRAO,
        help=f"máximo de invocações no ciclo (default: {FUSIVEL_PADRAO})",
    )
    rodar_cmd.add_argument(
        "--teto",
        type=int,
        default=TETO_PADRAO,
        help=f"máximo de tentativas por spec (default: {TETO_PADRAO})",
    )

    args = analisador.parse_args(argv)
    if args.subcomando == "repo":
        return _comando_repo(args, repo)
    if args.subcomando == "painel":
        return _comando_painel(args)
    if not args.subcomando:
        analisador.print_help()
        # Sair não-zero: sem subcomando nada rodou, e um script que encadeia
        # `sle` precisa saber disso pelo código, não pelo texto.
        raise SystemExit(2)

    config = Config(
        alvo=repos.resolver_cadastrado(args.alvo),
        specs=tuple(n.strip() for n in getattr(args, "specs", "").split(",") if n.strip()),
        seco=args.seco,
        fusivel=getattr(args, "fusivel", FUSIVEL_PADRAO),
        teto=getattr(args, "teto", TETO_PADRAO),
        comando=tuple(args.comando.split()),
        comando_interativo=tuple(args.comando_interativo.split()),
        pedidos=getattr(args, "pedidos", None),
    )

    segmento = rodar_pedidos if args.subcomando == "pedir" else rodar
    relato = segmento(config, executor=None)
    print(relato.texto)
    # Ensaio não falha: nada foi tentado, então não há o que reportar como
    # insucesso. Sem isto, `--seco` sai com 1 e envenena qualquer script que
    # encadeie `sle`.
    if config.seco:
        return 0
    return 0 if relato.final.decisao.motivo in GATES_PLANEJADOS else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
