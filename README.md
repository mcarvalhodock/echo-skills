# Spec Loop Engineering (SLE)

Disciplina pessoal para desenvolvimento assistido por IA que combina **Spec-Driven Development**, **BDD**, **TDD** e **Loop Engineering** em um único ciclo com invariantes explícitas — humano como árbitro nas decisões que não podem ser delegadas, agentes especializados nos passos onde a máquina executa melhor.

> **Status: em teste, v2 do método.** Sucessor direto do ECHO (versão 1, ainda presente aliás em `.echo/` para leitura histórica). O SLE nasceu da constatação de que o ECHO era, na prática, um caso de "loop engineering" bem estruturado — mas com três lacunas: papéis dos agentes borrados, enforcement probabilístico e fase de observação sem skill própria. Este repositório é a resposta a essas três lacunas.

---

## O que muda em relação ao ECHO

| Dimensão | ECHO (v1) | SLE (v2) |
| --- | --- | --- |
| Fases | 4 (Especificar, Codificar, Homologar, Observar) | 6 (Definir, Desenhar, Traduzir, Implementar, Homologar, Observar) |
| Skills | 3 (`especificar`, `planejar`, `homologar`) | 4 (`designer`, `validator`, `executor`, `observer`) |
| Papéis | Implícitos (skill = fase) | Explícitos (skill = papel; 4 invariantes deterministicamente checadas) |
| Enforcement | Probabilístico (prompt bem estruturado) | Determinístico (hooks in-session + CI de repositório) |
| Fase O | Prática manual | Skill própria com dois modos (event-driven / cadence-driven) |
| Nível de risco | 3 níveis (micro/padrão/complexo) | Mesmo esquema, com contrato arquitetural em N2/N3 e protótipo preservado em N3 |
| TDD | Universal | Contextualizado (`ortodoxo`/`parcial`/`manual`, declarado no manifesto) |

Tese completa em [`propostas/spec-loop-engineering.md`](./propostas/spec-loop-engineering.md). Guia de migração ECHO → SLE em [`docs/migracao-echo-sle.md`](./docs/migracao-echo-sle.md).

## As 4 invariantes

O SLE inteiro se apoia em quatro regras que **não são aspiracionais** — elas são verificadas por hooks e por CI:

1. **Designer ≠ Executor.** Quem desenha (spec, contrato arquitetural, protótipo) não escreve código de produção.
2. **Executor ≠ Validator.** Quem implementa não escreve os testes que validam a própria implementação.
3. **Nenhum agente é árbitro.** Decisões arquiteturais, disciplinares e de trade-off ficam com o humano em pontos explícitos ("gates").
4. **Observer é independente.** Quem observa e propõe reconciliações não é quem executou o que está sendo observado.

## O ciclo (6 fases, 4 skills)

```
Definir  ──┐
           ├─→ Designer   (spec + contrato arquitetural + protótipo N3)
Desenhar ──┘

Traduzir ──┐
           ├─→ Validator  (testes BDD + contrato + fidelidade / plano manual)
Homologar ─┘

Implementar ─→ Executor   (código de produção fiel à spec e aos testes)

Observar    ─→ Observer   (sinais, drift, propostas de reconciliação)
```

Regra de ouro:

> Nenhuma linha de código antes de existir contrato; nenhum teste antes de existir spec traduzível; nenhuma implementação antes de existir teste ou plano manual aprovado; nenhuma tarefa "pronta" sem verificação real e revisão humana.

Guia completo em [`metodologia-sle.md`](./metodologia-sle.md).

## O que tem neste repo

```
.
├── README.md
├── metodologia-sle.md              # o método explicado (sucessor de metodologia-echo.md)
├── template-especificacao.md       # spec em 3 níveis, com contrato arquitetural e fidelidade
├── dominios.md                     # catálogo canônico de domínios
├── .sle/
│   ├── manifesto.md                # domínios ativos + tdd-aplicavel + paths de produção
│   └── pressao-metodo.md           # log de pressão sistêmica sobre o método
├── .echo/                          # legado (v1) — manifesto redireciona para .sle/
├── designer/SKILL.md               # Fases D+D (Definir + Desenhar)
├── validator/SKILL.md              # Fases T+H (Traduzir testes + Homologar)
├── executor/SKILL.md               # Fase I (Implementar)
├── observer/SKILL.md               # Fase O (Observar)
├── tooling/
│   ├── hooks/                      # 3 hooks Python: enforcement in-session
│   └── ci/                         # 3 workflows: enforcement de repositório
├── propostas/
│   ├── spec-loop-engineering.md    # tese completa do SLE (v1..v4)
│   └── expansao-para-times.md      # hipótese não validada para escala
└── docs/
    ├── specs/                      # specs de features (incluindo a do próprio SLE)
    ├── plans/                      # planos de implementação
    └── migracao-echo-sle.md        # guia de migração (repositórios com ECHO instalado)
```

## Instalação das skills

**Claude Code:**

```bash
cp -r designer validator executor observer ~/.claude/skills/
```

Ou copie para `.claude/skills/` na raiz de um projeto para escopo local.

**Claude.ai:** zipe cada pasta de skill e faça upload em Settings → Features → Skills.

As skills se encadeiam por **handoff estrutural**: cada uma termina indicando explicitamente qual a próxima e em qual contexto (nova sessão) ela precisa rodar, para que a invariante "quem desenhou ≠ quem executa" seja preservada.

## Enforcement determinístico

O método não confia apenas na disciplina do humano ou na obediência do modelo. Existem duas camadas de checagem programática:

**Hooks in-session** (`tooling/hooks/`):

- `block-designer-writing-code` — bloqueia Designer escrevendo em `src/`, `lib/`, etc.
- `block-validator-writing-code` — bloqueia Validator escrevendo código de produção
- `block-executor-writing-tests-semantically` — Executor pode refactor não-semântico em testes (DRY, fixtures), mas bloqueia adição/remoção de teste ou mudança de assertion

Ativação em cada harness detalhada nos README de cada hook. Padrão de caminho de produção é declarado no `.sle/manifesto.md`.

**CI de repositório** (`tooling/ci/`):

- `spec-test-parity` — cada spec declara seus testes; cada teste declarado existe
- `criterion-coverage` — cada critério de aceite tem marcador em algum teste (ou em `manual-validation.md`)
- `pr-spec-diff` — código de produção não muda no PR sem que uma spec correspondente também mude

51 testes automatizados cobrem os dois pontos (bloqueio efetivo + não-interferência). Rode com `pytest tooling/` a partir da raiz do repositório.

## Como usar, no dia a dia

1. Peça a tarefa — a skill `designer` é invocada (ou chame `/designer` no Claude Code).
2. Ela classifica o risco (N1 micro / N2 padrão / N3 complexo) e conduz a Fase D+D:
   - N1: spec de 5 linhas; skip Desenhar
   - N2: spec padrão + contrato arquitetural
   - N3: spec enriquecida + contrato arquitetural + protótipo preservado (como artefato de fidelidade, não descartado)
3. Em Nível 2+, cada critério e caso de borda é classificado por [domínio](./dominios.md). Domínio endereça quem executa, não categoria do trabalho.
4. `designer` termina fazendo **handoff estrutural** para `validator`, em nova sessão.
5. `validator` traduz cada critério em teste (BDD + contrato arquitetural + fidelidade em N3) ou, quando TDD é parcial/manual (v3), cria um plano estruturado de validação manual (`docs/specs/<nome>-manual-validation.md`).
6. `validator` faz handoff para `executor`, em nova sessão.
7. `executor` implementa o código estritamente para passar os testes já escritos (ou executar o plano manual). Pode refactor não-semântico em testes se Clean Code exigir; não pode alterar semântica.
8. `executor` faz handoff de volta para `validator`, agora em Fase H (Homologar), que roda a suíte, executa o plano manual, confere critério por critério e conduz revisão arquitetural.
9. Após entrega, `observer` (event-driven ou em cadência semanal) reconcilia drift entre spec e código, extrai padrões emergentes e propõe atualizações no template — **sempre como sugestão para humano decidir**, nunca como decisão autônoma.

## O que ainda falta (honestamente)

- **Validação em escala real:** o método foi desenhado a partir da experiência com ECHO e das lacunas dele. Ainda não rodou em produção "sob pressão" suficiente para dizer que sobrevive a prazos apertados de time. Uso pessoal primeiro, difusão para time só depois de eu conseguir defender cada parte com exemplo real.
- **Granularidade real de hooks depende do harness:** os hooks são CLI portáveis, mas a integração fina com Claude Code / Cursor em 2026 ainda não é 100% estável. A camada de CI compensa, mas é enforcement mais tardio.
- **Observer é o papel mais novo e frágil:** ele tem skill própria (diferente de ECHO), mas ainda estamos aprendendo o formato ideal de saída para não virar "oráculo" que atropela decisão humana.

## Licença

Use como quiser. Isso é registro pessoal de processo, não produto — sem garantia, sem suporte formal, ajuste ao seu contexto.
