# Spec Loop Engineering (SLE)

Disciplina pessoal para desenvolvimento assistido por IA: **Spec-Driven Development** com duas invariantes que aguentam pressão, e nada além disso.

> **Status: v3 — uma subtração.** A v2 tinha 5 skills, 6 fases, 5 invariantes, 3 hooks e 6 tipos de artefato. Ela custava mais e entregava menos: em um ciclo real, produziu passagens, logs e registros suficientes para eu declarar uma spec "verde ponta a ponta" — e um pedido de dez linhas a um contexto limpo encontrou sete critérios não atendidos. Todo documento escrito entre esses dois pontos teve valor negativo: custou tokens e deu credibilidade a uma afirmação falsa.
>
> A v3 corta o que não se pagou. O resultado aterrissa perto do ECHO v1 (`especificar` / `planejar` / `homologar`), guardando a única coisa que a v2 acertou de verdade: **a atestação por leitura limpa**.

---

## O ciclo

| skill | entrega |
|---|---|
| `especificar` | plano específico da demanda — no máximo **15 critérios falsificáveis** |
| `codificar` | o código que satisfaz a spec, mais os testes **daquela demanda** |
| `verificar` | roda o que a demanda toca, e obtém veredito de **leitura limpa** |
| `homologar` | **no fim do desenvolvimento**: suíte completa e o checklist arquitetural |

`homologar` não roda por demanda. Cada demanda fecha em `verificar`; a suíte inteira roda uma vez, no fim — homologar cada spec contra a suíte completa é o custo que essa separação existe para evitar.

Método completo, em uma página: [`metodologia-sle.md`](./metodologia-sle.md).

## As duas invariantes

1. **O contrato precede a construção.** Spec escrita por quem já sabe como vai construir vira descrição, não contrato — e nenhuma verificação posterior detecta isso.
2. **Quem escreve não atesta.** `codificar` escreve os próprios testes, então a suíte verde é autoatestada. O antídoto é a leitura limpa dentro de `verificar`: dez linhas de molde fixo, contexto que não participou, saída em arquivo.

Não há hook de sessão, papel ativo nem fronteira de quem toca qual arquivo. Essas defesas custaram mais do que protegiam.

## O que tem neste repo

```
.
├── metodologia-sle.md          # o método, em uma página
├── dominios.md                 # catálogo canônico de domínios
├── especificar/SKILL.md
├── codificar/SKILL.md
├── verificar/SKILL.md
├── homologar/SKILL.md
├── .sle/manifesto.md           # domínios ativos + padrão de código + paths de produção
├── scripts/                    # instaladores (bash e PowerShell) + testes
├── tooling/ci/                 # workflows de enforcement de repositório
├── propostas/                  # tese histórica (v1..v4) — leitura, não vigente
└── docs/                       # specs, planos e guia de migração
```

## Instalação

```bash
./scripts/install.sh            # menu interativo
./scripts/install.ps1           # Windows
```

Ou manualmente, no Claude Code:

```bash
cp -r especificar codificar verificar homologar ~/.claude/skills/
```

Para escopo local, copie para `.claude/skills/` na raiz do projeto. No Claude.ai, zipe cada pasta e suba em Settings → Features → Skills.

## No dia a dia

1. **Conserto?** Se a régua é um comando com exit code que você escreve antes, nada novo persiste e nenhum contrato público muda — conserte e pronto. Sem spec, sem ciclo. As três perguntas são objetivas de propósito: enquanto o ônus for "justifique por que isto é barato", a resposta segura é sempre escalar.
2. `/especificar` — o plano. Você aprova antes de qualquer código.
3. `/codificar` — implementa e escreve os testes da demanda. Não roda a suíte completa.
4. `/verificar` — roda o que a demanda toca e abre a leitura limpa. Sem pergunta arquitetural.
5. Repita 2–4 por demanda.
6. `/homologar`, no fim — suíte inteira e o checklist que só você responde.

## O que ainda falta, honestamente

- **A v3 não rodou um ciclo inteiro ainda.** Ela nasceu do post-mortem da v2, e o teste é o próximo projeto real.
- **`homologar` no fim do desenvolvimento pressupõe que existe um fim.** Em produto contínuo, "fim" provavelmente vira cadência — e essa cadência ainda não está definida.
- **A leitura limpa custa um subagente por demanda.** É barata perto do que substituiu, mas não é grátis, e ainda não sei o piso de demanda em que ela deixa de valer.

## Licença

Use como quiser. Registro pessoal de processo, não produto — sem garantia, sem suporte formal, ajuste ao seu contexto.
