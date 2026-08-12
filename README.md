# Spec Loop Engineering (SLE)

Disciplina pessoal para desenvolvimento assistido por IA: **Spec-Driven Development** com duas invariantes que aguentam pressão, e nada além disso.

> **Status: v3 — uma subtração.** A v2 tinha 5 skills, 6 fases, 5 invariantes, 3 hooks e 6 tipos de artefato. Ela custava mais e entregava menos: em um ciclo real, produziu passagens, logs e registros suficientes para eu declarar uma spec "verde ponta a ponta" — e um pedido de dez linhas a um contexto limpo encontrou sete critérios não atendidos. Todo documento escrito entre esses dois pontos teve valor negativo: custou tokens e deu credibilidade a uma afirmação falsa.
>
> A v3 corta o que não se pagou. O resultado aterrissa perto do ECHO v1 (`especificar` / `planejar` / `homologar`), guardando a única coisa que a v2 acertou de verdade: **a atestação por leitura limpa**.
>
> O que cresceu depois foi **fora** do método: `tooling/loop/` automatiza o encadeamento entre as fases sem acrescentar nenhuma regra a elas. As quatro skills continuam sendo quatro prompts, e o loop continua sendo dispensável — dá para rodar tudo à mão.

---

## O ciclo

| skill | entrega |
|---|---|
| `especificar` | plano específico da demanda — no máximo **15 critérios falsificáveis** |
| `codificar` | o código que satisfaz a spec, mais os testes **daquela demanda** |
| `verificar` | roda o que a demanda toca, e obtém veredito de **leitura limpa** |
| `homologar` | **no fim do desenvolvimento**: suíte completa e o checklist arquitetural |

`homologar` não roda por demanda. Cada demanda fecha em `verificar`; a suíte inteira roda uma vez, no fim — homologar cada spec contra a suíte completa é o custo que essa separação existe para evitar.

Cada fase roda em **sessão limpa** e não invoca a seguinte. Quem encadeia é o loop (`tooling/loop/`) — ou você, à mão.

**Duas paradas por ciclo, e o número não cresce com o tamanho do lote:**

```
especificar × N → ┤aprovar o lote├ → (codificar → verificar) × N → homologar → ┤checklist├
     conversa                                    headless                headless
```

`especificar` é **interativa** de propósito: é a fase onde falta contexto, e o agente precisa perguntar. As outras rodam headless — lá a conversa não acrescenta, porque `codificar` tem a spec como contrato e `verificar` mede contra ela.

Método completo, em uma página: [`metodologia-sle.md`](./metodologia-sle.md).

## As duas invariantes

1. **O contrato precede a construção.** Spec escrita por quem já sabe como vai construir vira descrição, não contrato — e nenhuma verificação posterior detecta isso.
2. **Quem escreve não atesta.** `codificar` escreve os próprios testes, então a suíte verde é autoatestada. O antídoto é a leitura limpa dentro de `verificar`: dez linhas de molde fixo, contexto que não participou, saída em arquivo.

Não há hook de sessão, papel ativo nem fronteira de quem toca qual arquivo. Essas defesas custaram mais do que protegiam.

## O alvo

O método não mora no codebase que ele trabalha. Instala-se uma vez e opera sobre N codebases: o **alvo** é parâmetro de cada fase, e todo caminho — `docs/specs/`, `.sle/manifesto.md`, a suíte, o ref base — é relativo a ele. A exceção é [`dominios.md`](./dominios.md), que é do método e vale para todos.

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
├── scripts/sle, sle.ps1        # a ferramenta
├── scripts/install.*           # instaladores (bash e PowerShell) + testes
├── tooling/ci/                 # enforcement de repositório (2 workflows)
├── tooling/loop/               # o loop — decisão pura + driver ([guia](./tooling/loop/README.md))
├── propostas/                  # tese histórica (v1..v4) — leitura, não vigente
└── docs/                       # specs, vereditos, planos e guia de migração
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

O `sle` não precisa de instalação: Python 3.10+, sem dependência externa, rodando do clone. Mas ele **depende das skills instaladas**, porque cita cada uma pelo nome — e avisa quando a instalada divergir da do clone, que é erro fácil de cometer e caro de perceber.

## No dia a dia

1. **Conserto?** Se a régua é um comando com exit code que você escreve antes, nada novo persiste e nenhum contrato público muda — conserte e pronto. Sem spec, sem ciclo. As três perguntas são objetivas de propósito: enquanto o ônus for "justifique por que isto é barato", a resposta segura é sempre escalar.
2. `/especificar` — o plano. Você aprova antes de qualquer código.
3. `/codificar` — implementa e escreve os testes da demanda. Não roda a suíte completa.
4. `/verificar` — roda o que a demanda toca e abre a leitura limpa. Sem pergunta arquitetural.
5. Repita 3–4 por demanda do lote.
6. `/homologar`, no fim — suíte inteira e o checklist que só você responde.

Nada disso precisa ser digitado fase a fase. É para isso que existe o `sle`:

```bash
./scripts/sle pedir --alvo /projeto              # conversa, escreve as specs, para
                                                 # você lê e aprova
./scripts/sle rodar --alvo /projeto --specs a,b  # headless até o checklist
```

`pedir` lê `<alvo>/pedidos.md` — um `##` por demanda, o cabeçalho é o nome da spec — e abre uma sessão por pedido. `rodar` percorre o lote, commita cada tentativa de forma marcada, roda a suíte no fim e para no checklist. Comece pelo `--seco` nos dois.

Sai com **0** em gate planejado, **não-zero** em exceção — dá para encadear sem ler a saída. Guia completo (flags, monorepo, outro agente, o que cada parada significa, como limpar o histórico): [`tooling/loop/README.md`](./tooling/loop/README.md).

**Sem API key e sem SDK.** O loop fala com o CLI do agente por processo, um por fase. É isso que faz trocar de agente não mudar uma linha do roteamento.

## O que ainda falta, honestamente

- **O loop nunca invocou um agente de verdade.** Toda a suíte roda com executor falso, de propósito — nenhum teste chama `claude` nem `agent`, porque teste que depende de LLM não é régua, é aposta. O primeiro uso real é o teste que nenhuma suíte daqui faz.
- **A v3 não rodou um ciclo inteiro num projeto que não seja este.** Ela nasceu do post-mortem da v2, e se construiu aplicando o próprio método a si mesma; o teste é o próximo projeto real.
- **`homologar` no fim pressupõe que existe um fim.** Em produto contínuo, "fim" provavelmente vira cadência — e essa cadência ainda não está definida.
- **A leitura limpa custa um subagente por demanda.** É barata perto do que substituiu, mas não é grátis, e ainda não sei o piso de demanda em que ela deixa de valer.
- **Três dívidas reconhecidas e sem spec:** o campo `evidencia` da decisão carrega sete significados diferentes; `guarda-do-alvo` cobre cinco falhas distintas que ninguém distingue programaticamente; e `criterion_coverage` mantém um conjunto **global** de identificadores, então prefixo repetido entre specs esconde lacuna alheia.
- **`docs/specs/instaladores-sle.md` é da v2** e descreve skills que não existem mais. O CI acusa onze critérios descobertos por causa dela, e isso é honesto — a spec é que está velha.

## Licença

Use como quiser. Registro pessoal de processo, não produto — sem garantia, sem suporte formal, ajuste ao seu contexto.
