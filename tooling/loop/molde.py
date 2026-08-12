"""O molde da leitura limpa, com dono único.

Ele nasceu em prosa, dentro de `verificar/SKILL.md`, e a fase o emitia de
dentro da própria sessão. A auditoria é o primeiro lugar que precisa dele em
código — e duas cópias de um texto que ninguém amarra divergem, que foi
exatamente o que aconteceu entre skill instalada e skill do clone.

`test_molde.py` amarra estas linhas às daquele arquivo: mudar uma sem a outra
reprova a suíte.

Puro: monta texto, não toca nada.
"""

from __future__ import annotations

# As duas linhas do meio são invariantes do molde — o vocabulário do veredito e
# a proibição de sugerir correção. É por elas que a régua compara.
CLASSIFICACAO = (
    'Para cada critério, uma linha "- **<ID>** — atendido|não atendido|'
    'não verificável", e o porquê depois.'
)
LIMITE = "Não sugira correção. Não leia mais nada."


def contra_estado_atual(spec: str, escopo: str, saida: str) -> str:
    """A variante sem diff: a mesma que vale para alvo sem git."""
    return "\n".join(
        [
            f"Leia {spec} e o estado atual de {escopo}.",
            CLASSIFICACAO,
            LIMITE,
            f"Saída em {saida}.",
        ]
    )
