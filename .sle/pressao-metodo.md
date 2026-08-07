# Log de pressão sobre o método SLE

> Instrumento de evolução do próprio método, análogo ao [`pressao-catalogo.md`](./pressao-catalogo.md) (que existe para o vocabulário de domínios). Este log captura pressões **sistêmicas** — não sobre um domínio isolado, mas sobre o funcionamento do SLE como um todo.
>
> **Localização canônica:** `.sle/pressao-metodo.md`. Repositórios legados podem usar `.echo/pressao-metodo.md` como alias — as skills leem `.sle/` primeiro; se ausente, caem para `.echo/`.

## Para que serve

O SLE tem quatro papéis operando em separação estrutural, três invariantes de enforcement, três camadas de rigor de teste, e várias regras que dependem de julgamento. Nenhuma dessas peças é infalível — algumas são deliberadamente permissivas (degrada, não bloqueia). Este log é o único instrumento que revela quando e como o método está sob pressão.

**Cada entrada aqui é um sinal para a Fase Observar.** Um caso ocasional é ruído; padrão persistente é dado para agregação (A4) e potencialmente para reforma do método.

## Tipos de entrada

Este log recebe múltiplos tipos de entrada, cada um proveniente de uma skill diferente. **A estrutura das colunas varia por tipo** — cada seção abaixo tem sua própria tabela.

### Tipo A — Retorno do Validador (spec vaga / não-falsificável)

Origem: `validator/SKILL.md`, Passo 2 (Gate de tradutibilidade). Quando o Validator identifica que um item da spec não é tradutível em teste executável, ele devolve a spec ao Designer e registra aqui.

| data | spec | itens devolvidos | motivo em uma frase |
|---|---|---|---|

*(sem registros até o momento)*

### Tipo B — Item que caiu em validação manual (v3)

Origem: `validator/SKILL.md`, Passo 3.1. Quando o repositório declara `tdd-aplicavel: parcial` ou `manual` no manifesto, cada item da spec que não vira teste automatizado (e vira passo manual em `manual-validation.md`) é registrado aqui. Padrão persistente ("essa codebase vive em manual") é sinal para reflexão sobre modernização.

| data | spec | item | tag (@criterio / @contrato / @fidelidade) | motivo em uma frase |
|---|---|---|---|---|

*(sem registros até o momento)*

### Tipo C — Retorno do Executor (bug semântico em teste ou passo manual, v4)

Origem: `executor/SKILL.md`, bloco "Regra de ouro operacional — poder estrutural de retorno". Quando o Executor identifica bug semântico em teste automatizado ou passo manual, ele devolve ao Validator e registra aqui. Padrão persistente ("Validador X faz muito teste ruim") é sinal para calibrar como o Validator escreve testes.

| data | spec | artefato | tipo de problema | justificativa em uma frase |
|---|---|---|---|---|

*(sem registros até o momento)*

Legenda de tipos de problema:
- `bug de assertion` — teste verifica valor errado
- `mock errado` — mock/stub configurado de forma que muda lógica do setup
- `cobertura incorreta` — tag do teste diz cobrir X, mas verifica Y
- `passo impossível` — passo M[n] pede ação que não faz sentido (dependência ausente, comando inexistente, evidência incoerente)

### Tipo D — Decisão humana de pular Gate 3 arquitetural

Origem: `validator/SKILL.md`, Passo 10 (Gate humano 3). Quando o humano opta por pular a revisão arquitetural, o Validador registra aqui. Padrão persistente ("humano sempre pula") é sinal de que Gate 3 pode estar mal-desenhado, ou de que a disciplina de revisão precisa recalibração.

| data | spec | motivo declarado pelo humano (opcional) |
|---|---|---|

*(sem registros até o momento)*

### Tipo E — Retrospectiva do Observer (A4 agregado)

Origem: `observer/SKILL.md`, Passo 5 (fluxo cadência-driven). Retrospectiva periódica do Observer agrega padrões observados no período. Diferente dos tipos A-D (que são pontuais), Tipo E é **agregação** — o Observer lê os tipos A-D acumulados e destila padrão.

### Retrospectiva [período: AAAA-MM-DD a AAAA-MM-DD]

*(estrutura livre — segue o formato do output A4 do Observer)*

*(sem retrospectivas até o momento)*

### Tipo F — Ajuste do próprio método (excepcional)

Origem: humano decide que o método precisa mudança concreta após uma retrospectiva Tipo E ou um sinal externo. Ajustes de método deste tipo mudam skills, template, manifesto ou tese — cada ajuste é registrado com data, motivo, e escopo dos arquivos alterados.

Estes ajustes ficam também documentados como "histórico de revisões" na tese (`propostas/spec-loop-engineering.md`) — este log é a entrada resumida com pointer.

### Tipo G — Sinal de fricção do humano usando o método

Origem: humano (praticante do SLE) durante uso real, fora de fase específica. Diferente dos tipos A-D (originados por skills operacionais), Tipo G é **dado do usuário direto sobre a experiência de adoção/uso** do método — instalação, onboarding de time, esforço por sessão, integração com harness, etc. Não é bug do código nem falha de spec: é fricção percebida.

Padrão persistente (mesmo tipo de fricção mencionado em várias entradas Tipo G) é sinal forte para agregação em retrospectiva Tipo E e potencialmente ajuste Tipo F. Uma entrada isolada é ruído; três entradas com o mesmo diagnóstico são pressão para reforma.

| data | contexto | sinal em uma frase | pontos de fricção observados | destino sugerido |
|---|---|---|---|---|
| 2026-08-07 | Instalador SLE por projeto | Setup completo (skills + hooks + CI + marker file + config harness) é oneroso demais para adoção por equipes | (1) `.sle/.active-role` manual por sessão sem produtor automático; (2) copia-e-cola de snippet no config do harness sem merge inteligente; (3) preencher 6-8 placeholders no manifesto sem autodetecção; (4) cada dev novo do time refaz o setup se instalação for global; (5) exige clone prévio do repositório `echo-skills` como fonte | (a) documentar padrão "instalação local + commit = adoção zero-config para o time"; (b) spec N2 para wizard de manifesto com autodetecção; (c) spec N2 para modo "lite" (só skills, sem hooks nem CI); (d) revisitar Estratégia C (wrapper de invocação) quando houver ≥3 sinais Tipo G sobre o marker file |

| data | ajuste | motivo em uma frase | escopo | pointer para detalhe |
|---|---|---|---|---|
| 2026-08-07 | v2 (fidelidade) | protótipo N3 descartado gerava frustração contratual | designer, validator, executor, tese, spec, plano | tese, seção "Histórico de revisões" |
| 2026-08-07 | v3 (TDD contextualizado) | codebases legadas não suportam TDD ortodoxo | validator, tese, spec, plano | tese, seção "Histórico de revisões" |
| 2026-08-07 | v4 (Clean Code universal + refactor não-semântico) | testes ruins do Validator geravam custo de manutenção; Executor deve poder refatorar | executor, validator, tese, spec, plano | tese, seção "Histórico de revisões" |
| 2026-08-07 | Instaladores automatizados + mitigação parcial da lacuna "role sem produtor" | hooks pedem `--role` mas nenhum componente do sistema o produz automaticamente; instalador agora configura marker-file (`.sle/.active-role`) + `.gitignore` + `SLE-SETUP.md` com instruções por harness, tornando a Estratégia B (marker-file) o caminho padrão do repositório consumidor | scripts/, docs/specs/instaladores-sle*.md, docs/plans/instaladores-sle.md, scripts/tests/ | docs/specs/instaladores-sle.md, seção "Observações para a Fase O" |

**Nota sobre a lacuna "role sem produtor":** a mitigação acima é **parcial**. Fechamento completo exigiria um wrapper de invocação (Estratégia C) que expõe `SLE_ACTIVE_ROLE` como variável de ambiente ao processo do harness antes da skill ser carregada. Isso está fora do escopo v1 do instalador porque cada harness (Claude Code, Cursor, futuros) tem contrato próprio de wrapper — precisa de investigação por harness antes de virar automação. Registrar como pressão recorrente se aparecer em uso real com hooks sendo burlados por marker-file esquecido.

## Formato geral

- **data** — quando o sinal aconteceu, em `AAAA-MM-DD`
- **spec** — qual especificação estava em curso (quando aplicável)
- Colunas específicas variam por tipo (ver seções acima)

## Como usar este log

**Escrita:** cada skill que gera pressão sabe qual seção usar (declarado nos passos correspondentes das skills). Se você está anotando manualmente, use o formato da seção apropriada.

**Leitura:** o Observer é o principal cliente deste log em modo cadência-driven. Você (humano) também pode ler diretamente para calibração disciplinar (Atividade A5, não delegável ao Observer).

**Curadoria:** o log cresce sem podas automáticas. A retrospectiva periódica do Observer produz Tipo E que resume e aponta padrões — mas as entradas Tipo A-D originais permanecem. Se o arquivo ficar grande demais, considere arquivar por período (`.sle/pressao-metodo-2026-H1.md`) mantendo apenas o período corrente ativo.
