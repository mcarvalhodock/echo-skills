"""Hook: block-validator-writing-code.

Enforcement da segunda invariante do SLE, na redação v5:
**ninguém assina o que escreveu**.

A v4 dizia "o Validator nunca escreve código de produção", e este hook
bloqueava por path. O eixo estava errado: proibir *escrever* gerava cerimônia
sem comprar segurança, e o que sustenta o generator/evaluator separation é
proibir *atestar*. Consertar não é contaminação — consertar é o objetivo.

A v5 separa os dois atos, e este hook passa a enforçar a separação:

- Escrever código de produção é **permitido em emenda** dirigida pelo humano.
- A emenda só passa se a dívida de atestação já estiver **registrada** no
  log de pressão do método. Escrever sem declarar que não pode assinar é
  exatamente o que a invariante proíbe, e é o que continua bloqueado.

O que o hook consegue verificar é o registro; quem de fato assina é humano.
Por isso a checagem é: existe, no log, uma linha que nomeia esta spec e a
marca como atestação não-independente?

Durante a Fase Traduzir não existe emenda possível — não há código ainda, e o
Validator implementando por conta própria destrói a suíte que ele deveria
estar derivando da spec. Passe --fase traduzir e o bloqueio é incondicional.

Uso via CLI:
    python hook.py --role <role> --path <path> --action <action>
                   [--emenda <spec>] [--fase <traduzir|homologar>]
                   [--manifesto <path>] [--project-root <path>]

Exit codes:
    0 = operação permitida
    1 = operação bloqueada (motivo em stdout)
    2 = erro de invocação
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_PRODUCTION_PATH_PATTERNS: tuple[str, ...] = (
    r"^src/",
    r"^lib/",
    r"^app/",
    r"^internal/",
    r"^pkg/",
    r"^cmd/",
)

ALLOWED_VALIDATOR_PATH_PATTERNS: tuple[str, ...] = (
    r"^tests?/",
    r"^spec/",
    r"^__tests__/",
    r"^docs/specs/.*-log\.md$",
    r"^docs/specs/.*-manual-validation\.md$",
    r"^docs/specs/.*-fidelidade\.md$",
    r"^\.sle/pressao-metodo\.md$",
    r"^\.sle/pressao-catalogo\.md$",
    r"^\.echo/pressao-catalogo\.md$",
)


"""Como o registro declara que a atestação não é independente.

Aceita com e sem acento porque log é escrito à mão, e recusar uma emenda por
causa de um acento seria a cerimônia que a v5 veio tirar do caminho.
"""
MARCADORES_DE_NAO_INDEPENDENCIA: tuple[str, ...] = (
    "não-independente",
    "nao-independente",
    "não independente",
    "nao independente",
)


def is_production_path(rel_path: str, patterns: tuple[str, ...]) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in patterns)


def is_validator_allowed_path(rel_path: str) -> bool:
    normalized = rel_path.replace("\\", "/").lstrip("./")
    return any(re.match(p, normalized) for p in ALLOWED_VALIDATOR_PATH_PATTERNS)


def read_production_patterns_from_manifest(
    manifesto_path: Path,
) -> tuple[str, ...]:
    if not manifesto_path.exists():
        return DEFAULT_PRODUCTION_PATH_PATTERNS

    content = manifesto_path.read_text(encoding="utf-8")
    match = re.search(
        r"##\s+Paths?\s+de\s+produ[cç][aã]o\s*\n(.+?)(?:\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if not match:
        return DEFAULT_PRODUCTION_PATH_PATTERNS

    declared: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            declared.append(stripped[2:].strip("`").strip())

    return tuple(declared) if declared else DEFAULT_PRODUCTION_PATH_PATTERNS


def localizar_log_de_pressao(project_root: Path) -> Path:
    """O log canônico, com o alias legado como segunda tentativa."""
    canonico = project_root / ".sle" / "pressao-metodo.md"
    if canonico.exists():
        return canonico

    legado = project_root / ".echo" / "pressao-metodo.md"
    return legado if legado.exists() else canonico


def emenda_registrada(log_path: Path, spec: str) -> bool:
    """A dívida de atestação desta spec já está declarada no log?

    Exige as duas coisas na MESMA linha: o identificador da spec e a marca de
    não-independência. Uma emenda registrada para outra spec não autoriza esta,
    e uma linha que cita a spec sem admitir quem assina não é declaração — é
    menção.
    """
    if not log_path.exists():
        return False

    alvo = spec.strip().casefold()
    if not alvo:
        return False

    for linha in log_path.read_text(encoding="utf-8").splitlines():
        dobrada = linha.casefold()
        if alvo in dobrada and any(
            marcador in dobrada for marcador in MARCADORES_DE_NAO_INDEPENDENCIA
        ):
            return True

    return False


def evaluate(
    role: str,
    path: str,
    action: str,
    manifesto_path: Path,
    emenda: str | None = None,
    fase: str | None = None,
    log_path: Path | None = None,
) -> tuple[int, str]:
    if role != "validator":
        return 0, f"hook não se aplica: role={role}"

    if action not in {"write", "edit", "delete"}:
        return 0, f"hook não se aplica: action={action}"

    if is_validator_allowed_path(path):
        return 0, f"path permitido para validator: {path}"

    production_patterns = read_production_patterns_from_manifest(manifesto_path)
    if not is_production_path(path, production_patterns):
        return 0, f"path fora do escopo de produção declarado: {path}"

    if fase and fase.strip().casefold() == "traduzir":
        return (
            1,
            (
                f"BLOQUEADO: Validator escrevendo código de produção na Fase "
                f"Traduzir. Caminho '{path}' bate com padrão de produção do "
                f"repositório.\n"
                f"Aqui não existe emenda possível: não há código ainda, e "
                f"implementar por conta própria destrói a suíte que você deveria "
                f"estar derivando da spec. Escreva a régua; o 'executor' "
                f"implementa depois, em outra sessão."
            ),
        )

    if emenda is None:
        return (
            1,
            (
                f"BLOQUEADO: Validator (skill do SLE) alterando código de produção "
                f"sem emenda declarada. Caminho '{path}' bate com padrão de "
                f"produção do repositório. Invariante 2 do SLE (v5): ninguém "
                f"assina o que escreveu.\n"
                f"Escrever é permitido; escrever calado não é. Dois caminhos:\n"
                f"(a) handoff para o Executor em nova sessão — é o de maior "
                f"independência, e o default quando o critério está claro e certo;\n"
                f"(b) emenda dirigida pelo humano — registre a dívida no log de "
                f"pressão e reinvoque com --emenda <spec>.\n"
                f"Sem --emenda, o hook não tem como saber que a atestação daquele "
                f"critério ficou marcada como não-independente."
            ),
        )

    alvo_do_log = log_path if log_path is not None else Path(".sle/pressao-metodo.md")
    if not emenda_registrada(alvo_do_log, emenda):
        return (
            1,
            (
                f"BLOQUEADO: emenda de '{emenda}' declarada, mas não registrada em "
                f"'{alvo_do_log}'.\n"
                f"O registro é a parte barata e é a única que o hook consegue "
                f"verificar — sem ele, 'a spec mudou' vira a explicação universal "
                f"para 'o código não fez o que a gente disse'.\n"
                f"Acrescente uma linha que nomeie '{emenda}' E marque a atestação "
                f"como não-independente, no formato da seção 'Emenda' da skill "
                f"validator:\n"
                f"| data | spec | item | o que mudou | quem pediu | atestação |\n"
                f"| ... | {emenda} | @criterio:X | critério/régua/código | humano | "
                f"não-independente |"
            ),
        )

    return (
        0,
        (
            f"PERMITIDO em emenda: '{path}' para a spec '{emenda}', com a dívida "
            f"de atestação registrada em '{alvo_do_log}'.\n"
            f"Lembrete da invariante 2: você acabou de perder o direito de dizer "
            f"que este critério foi verificado de forma independente. Diga isso no "
            f"relatório, e não só no log."
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--manifesto", default=None)
    parser.add_argument(
        "--emenda",
        default=None,
        help=(
            "identificador da spec sendo emendada. Exige registro prévio da "
            "dívida de atestação no log de pressão do método."
        ),
    )
    parser.add_argument(
        "--fase",
        default=None,
        help="traduzir | homologar. Em 'traduzir' o bloqueio é incondicional.",
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()
    manifesto_path = (
        Path(args.manifesto).resolve()
        if args.manifesto
        else project_root / ".sle" / "manifesto.md"
    )
    if not manifesto_path.exists():
        legacy = project_root / ".echo" / "manifesto.md"
        if legacy.exists():
            manifesto_path = legacy

    exit_code, message = evaluate(
        role=args.role,
        path=args.path,
        action=args.action,
        manifesto_path=manifesto_path,
        emenda=args.emenda,
        fase=args.fase,
        log_path=localizar_log_de_pressao(project_root),
    )
    print(message)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
