# Manifesto SLE — echo-skills

> Formato e regras em [`dominios.md`](../dominios.md). Este arquivo é a declaração real deste repositório, não um exemplo — o exemplo de preenchimento vive no catálogo.
>
> **Localização canônica:** `.sle/manifesto.md`. Alias legado (`.echo/manifesto.md`) permanece com nota de redirect para transições de repositório antigo — as skills leem `.sle/` primeiro; se ausente, caem para `.echo/`.

## Domínios ativos

**`plataforma` e `integração`** (após conclusão da refatoração para SLE).

O método ganhou componente executável: hooks de enforcement, CI workflows, subagent configs. Isso ativa `plataforma` (deploy/runtime dos componentes executáveis) e `integração` (interface com harnesses como Claude Code, Cursor, GitHub Actions).

Isto é uma declaração, não uma pendência: as próximas specs deste repositório poderão fatiar por esses domínios se atenderem às condições de fatiabilidade (pluralidade, independência, massa) — o que muitos não vão fazer, e é normal.

## Domínios inativos

| domínio | por quê |
|---|---|
| `segurança` | não há authn, autorização ou segredo — o repositório é público por natureza |
| `privacidade` | não trata dado pessoal de ninguém |
| `dados` | não há schema, migração ou persistência |
| `experiência` | não há interface; o consumo é por leitura de markdown e invocação de skill |

## Ferramental disponível

- Git (repositório versionado, branch de trabalho: `refatoracao/spec-loop-engineering`).
- Editor Markdown (declaração pura de método continua sendo o núcleo do repositório).
- Python (para scripts de hook, quando começarem a existir em `tooling/hooks/`).
- Shell (Windows/PowerShell no ambiente do autor; scripts também disponíveis em `.sh` quando existirem, para portabilidade).
- GitHub Actions (ou equivalente) para CI, com templates em `tooling/ci/` que os repositórios consumidores podem adaptar.

## Padrão de código local

Não se aplica a este repositório (markdown puro + scripts de tooling em Python futuro). O padrão declarado aqui serve de **exemplo de campo obrigatório para repositórios consumidores** — cada projeto que adota SLE declara aqui o seu:

- Referência ao `STYLE.md`, `.editorconfig`, `.cursor/rules/`, `linter.config`, ou similares
- Convenções específicas de nomenclatura, tamanho de função, complexidade
- Ferramentas de formatação/linting que rodam localmente

Ausência do campo degrada, não bloqueia — o Executor assume boas práticas gerais e sinaliza uma vez.

## Hooks ativos

Nenhum ainda. Fase 7 do plano de refatoração adiciona hooks em `tooling/hooks/` e este campo passará a listá-los:

- `block-designer-writing-code/` (previsto)
- `block-executor-writing-tests-semantically/` (previsto — permite refactor não-semântico via detecção suíte antes/depois)
- `block-validator-writing-code/` (previsto)

## CI templates ativos

Nenhum ainda. Fase 7 adiciona em `tooling/ci/`:

- `spec-test-parity.yml` (previsto — spec ↔ test file 1-para-1)
- `criterion-coverage.yml` (previsto — cobertura de crítério por tag)
- `pr-spec-diff.yml` (previsto — PR modifica código sem diff em spec é bloqueado)

## Nível de rigor esperado

**Produção crítica.** Este repositório declara e materializa metodologia usada em outros projetos — mudanças estruturais têm efeito multiplicador. Cabe rigor de N3 mesmo em tarefas que pareceriam N2 em outros contextos.

## `tdd-aplicavel`

**`ortodoxo`** (default do SLE).

Justificativa: o próprio repositório do método deve praticar o rigor que prescreve. Skills futuras que gerarem código executável em `tooling/` devem vir acompanhadas de suite automatizada com falhas antes da implementação, seguindo TDD clássico.

Se, no futuro, algum componente de `tooling/` (ex: hook complexo com integração de harness) for genuinamente difícil de automatizar, este campo pode ser reavaliado — mas seria um recuo do rigor do método aplicado a si mesmo, e precisaria de justificativa registrada em `.sle/pressao-metodo.md`.

## Donos

Não se aplica — repositório de uso pessoal. Ver [`propostas/expansao-para-times.md`](../propostas/expansao-para-times.md) para o raciocínio sobre aprovador nomeado por domínio, que segue como hipótese não validada.

## Quando este manifesto muda

- Chegada de novos hooks/CI templates: campos "Hooks ativos" e "CI templates ativos" ganham entradas.
- Reavaliação de rigor (raro): mudança do campo "Nível de rigor esperado" ou `tdd-aplicavel` exige justificativa registrada em `.sle/pressao-metodo.md`.
- Domínios ativos podem crescer se a superfície do repositório crescer (ex: se `segurança` passar a ser relevante quando hooks acessarem tokens externos).

## Histórico

- **2026-08-07:** manifesto criado como parte da refatoração ECHO → SLE. Domínios `plataforma` e `integração` promovidos de inativos a ativos (o método ganhou componente executável). Campo `tdd-aplicavel` adicionado no ajuste v3.
