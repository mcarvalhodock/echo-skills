# versao-limpa-das-skills — veredito

Base: `1396c4f45aa89d96962d4ab0c67707dee76cb0a0..HEAD`, escopo `..`.

- **C1** — atendido

  O texto da spec (`docs/specs/versao-limpa-das-skills.md`, novo neste diff) registra literalmente a decisão do gate — "formato genérico único para qualquer harness, preservando os princípios já vigentes do método" (linha do C1) — e o Contrato técnico traduz "manter todos os princípios atuais" em invariante explícita: altera portabilidade/compatibilidade entre harnesses, sem alterar fases, invariantes ou gates do método. O `README.md` acompanha com a seção "Formato das skills — genérico único, para qualquer harness", que fixa o contrato em duas chaves (`name`, `description`) e afirma "nada específico de harness".

- **C2** — atendido

  Nos seis `SKILL.md` (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`, `prototipar-frontend`) o frontmatter foi convertido de descrição em linha única para bloco YAML folded (`description: >-` seguido de linhas indentadas). Essa forma é aceita por `yaml.safe_load` estrito — inclusive nas frases que contêm `: ` no meio, que era o defeito histórico. O teste `TestC2FrontmatterYAMLValida` em `tests/test_versao_limpa_das_skills.py` parametriza exatamente essa carga para as seis.

- **C3** — atendido

  As três antes quebradas (`especificar`, `codificar`, `prototipar-frontend`) passaram a usar o mesmo molde folded `description: >-` que as outras três; o conjunto de chaves ficou `{name, description}` para todas. Não há caminho ramificado por skill: o mesmo parser YAML estrito abre as seis, e `TestC3CarregamNoMesmoMecanismo::test_todas_as_seis_compartilham_o_mesmo_conjunto_de_chaves` trava essa uniformidade.

- **C4** — atendido

  O diff remove a linha `disable-model-invocation: false` dos seis `SKILL.md` (uma remoção por arquivo, sem contrapartida em outro lugar do repositório). O teste `TestC4DisableModelInvocationRemovido` cobre a ausência tanto no frontmatter carregado quanto no texto bruto do arquivo — este último para impedir reintrodução silenciosa por copy-paste. "Sem regressão de comportamento" é o que sobra, e o diff não altera nada além dessa chave e da reformulação de `description` — nenhum outro contrato do arquivo foi tocado.

- **C5** — atendido

  Nos três arquivos em `.claude/agents/` (`sle-codificar.md`, `sle-verificar.md`, `sle-homologar.md`) o diff remove a linha `tools: Read, Write, Edit, Glob, Grep, Bash[, Agent]` — a especialização Claude-específica — e converte `description` para o mesmo bloco folded `>-`. O frontmatter resultante tem exatamente `{name, description}`, batendo com o contrato de C1. `TestC5AgentesSeguemFormatoGenerico::test_frontmatter_so_tem_name_e_description` fixa esse conjunto de chaves como igualdade estrita.

- **C6** — atendido

  A nova seção do `README.md` afirma explicitamente: "A **fonte versionada** deste repositório passa a ser suficiente para o fluxo atual: o carregamento das skills não depende de cópia antiga em `~/.claude/skills/` estar presente ou atualizada." O critério pede que o repositório deixe de depender dessa cópia para funcionar no fluxo atual, e a documentação operacional passa a declarar isso como contrato. `TestC6FonteVersionadaSuficiente` cobre ambas as afirmações no README (o "fonte versionada" e o "não depende … `~/.claude/skills/`").

- **C7** — atendido

  O `README.md` ganhou a seção "Validar a carga das seis skills", com o comando concreto (`python -m pytest tests/test_versao_limpa_das_skills.py -v`), a lista das seis skills nomeadas, o que o teste mede (C2/C3/C8, C4, C5) e a conferência complementar no painel de skills do Cursor. `TestC7DocumentacaoDeValidacaoDeCarga` valida a existência da seção pesquisável e a nomeação do harness (Cursor).

- **C8** — atendido

  A medida física do pré-requisito — "as seis skills carregam" — coincide com a de C2 e está atendida pelas mesmas evidências: o parser YAML estrito abre os seis frontmatters no molde uniforme. `TestC8PreRequisitoDoPluginCursorAtendido` re-testa isso do ângulo do consumidor (`plugin-cursor`), deixando o vínculo explícito no vereditos das duas specs. Nada em `docs/specs/plugin-cursor.md` foi tocado neste diff — nem precisa, porque C8 é uma afirmação sobre o pré-requisito ficar resolvido, não sobre a spec dependente.
