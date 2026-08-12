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
- Python 3.12 + pytest (scripts de CI em `tooling/ci/scripts/` e o roteador do loop em `tooling/loop/`).
- Shell (Windows/PowerShell no ambiente do autor; scripts também disponíveis em `.sh` quando existirem, para portabilidade).
- GitHub Actions (ou equivalente) para CI, com templates em `tooling/ci/` que os repositórios consumidores podem adaptar.

## Padrão de código local

Não se aplica a este repositório (markdown puro + scripts de tooling em Python futuro). O padrão declarado aqui serve de **exemplo de campo obrigatório para repositórios consumidores** — cada projeto que adota SLE declara aqui o seu:

- Referência ao `STYLE.md`, `.editorconfig`, `.cursor/rules/`, `linter.config`, ou similares
- Convenções específicas de nomenclatura, tamanho de função, complexidade
- Ferramentas de formatação/linting que rodam localmente

Ausência do campo degrada, não bloqueia — o Executor assume boas práticas gerais e sinaliza uma vez.

## Hooks ativos

**Nenhum.** Os três hooks de enforcement de papel foram removidos na v3: custaram mais do que protegiam, e a v2 blindada por eles produziu um "verde ponta a ponta" com sete critérios não atendidos. Blindagem não comprou correção.

A separação de papéis hoje é comprada por **sessão limpa por fase** — que é isolamento de contexto, não de escrita. Se um hook voltar, ele mora no driver do loop, não no método.

## CI templates ativos

Dois workflows GitHub Actions em `tooling/ci/`, com scripts Python portáveis:

- [`tooling/ci/criterion-coverage.yml`](../tooling/ci/criterion-coverage.yml) — cada critério (`A1`, `C2`, `L3`, …) tem marcador `spec:<ID>` em algum teste ou em `-manual-validation.md`
- [`tooling/ci/pr-spec-diff.yml`](../tooling/ci/pr-spec-diff.yml) — código de produção não muda no PR sem que uma spec correspondente também mude

Cobertura: 14 testes em `tooling/ci/tests/`.

`spec-test-parity` foi aposentado: exigia uma seção `## Testes vinculados` que o formato v3 não tem. Ver `tooling/ci/README.md`.

Neste repositório os workflows estão presentes como referência canônica — não estão habilitados em `.github/workflows/`. Repositórios consumidores copiam para lá e ajustam os paths de produção do próprio manifesto.

## Paths de produção

Lidos por `pr_spec_diff`. Aqui, "produção" é o que outros repositórios consomem:

- `^tooling/`
- `^scripts/`
- `^(especificar|codificar|verificar|homologar)/`

## Loop

`tooling/loop/` — o roteador que decide a próxima transição do ciclo a partir do estado observável, para que o humano deixe de ser o barramento de mensagens entre as fases. Núcleo determinístico e puro (`roteador.py`, `veredito.py`), registro em JSONL (`registro.py`). Specs em `docs/specs/roteador-*.md`.

O loop mora **com o método**, não nos repositórios-alvo: ele recebe o alvo por parâmetro e opera sobre N codebases. O instalador não o copia para o consumidor, e isso é deliberado.

Guia operacional em [`tooling/loop/README.md`](../tooling/loop/README.md).

## Nível de rigor esperado

**Produção crítica.** Este repositório declara e materializa metodologia usada em outros projetos — mudanças estruturais têm efeito multiplicador. Cabe rigor de N3 mesmo em tarefas que pareceriam N2 em outros contextos.

## `tdd-aplicavel`

**`ortodoxo`** (default do SLE).

Justificativa: o próprio repositório do método deve praticar o rigor que prescreve. Skills futuras que gerarem código executável em `tooling/` devem vir acompanhadas de suite automatizada com falhas antes da implementação, seguindo TDD clássico.

Se, no futuro, algum componente de `tooling/` (ex: hook complexo com integração de harness) for genuinamente difícil de automatizar, este campo pode ser reavaliado — mas seria um recuo do rigor do método aplicado a si mesmo, e precisaria de justificativa registrada em `.sle/pressao-metodo.md`.

## Donos

Não se aplica — repositório de uso pessoal. Ver [`propostas/expansao-para-times.md`](../propostas/expansao-para-times.md) para o raciocínio sobre aprovador nomeado por domínio, que segue como hipótese não validada.

## Quando este manifesto muda

- Chegada ou remoção de CI templates: o campo "CI templates ativos" acompanha. Um verificador que deixa de ler o formato vigente é defeito, não desatualização.
- Reavaliação de rigor (raro): mudança do campo "Nível de rigor esperado" ou `tdd-aplicavel` exige justificativa registrada em `.sle/pressao-metodo.md`.
- Domínios ativos podem crescer se a superfície do repositório crescer (ex: se `segurança` passar a ser relevante quando hooks acessarem tokens externos).

## Histórico

- **2026-08-07:** manifesto criado como parte da refatoração ECHO → SLE. Domínios `plataforma` e `integração` promovidos de inativos a ativos (o método ganhou componente executável). Campo `tdd-aplicavel` adicionado no ajuste v3.
- **2026-08-07 (fim do dia):** Fase 7 concluída — três hooks (`tooling/hooks/`) e três workflows CI (`tooling/ci/`) entregues com 51 testes verdes.
- **2026-08-11:** v3 do método. Cinco skills viram quatro, os três hooks e `tooling/hooks/` saem inteiros, e sobram duas invariantes e um artefato (o veredito).
- **2026-08-12:** sessão limpa por fase e o conceito de **alvo** entram no método; nasce `tooling/loop/`. `criterion_coverage` é corrigido — o padrão dele era o da v2 e lia **zero** critérios numa spec v3, reportando sucesso sobre spec que não conseguia abrir. `spec_test_parity` é aposentado.
