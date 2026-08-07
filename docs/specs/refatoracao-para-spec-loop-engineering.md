# Spec: Refatoração ECHO → Spec Loop Engineering (SLE)

> **Nível 3 — Complexo.** Muda identidade do repositório, adiciona componente executável, refatora skills já usadas em produção pessoal. Cabe todo o rigor de N3.
>
> **v2 — 2026-08-07 (ajuste durante Fase C).** Durante a implementação (Passos 2–5 do plano), foi identificada a *fissura da fidelidade*: protótipo descartado em N3 gera frustração contratual entre o que foi homologado e o que é implementado. Ajuste aplicado à tese ([v2 do documento base](../../propostas/spec-loop-engineering.md)) e refletido aqui: (a) critério A5 novo — regras de acesso ao protótipo preservado; (b) critério C1 ampliado — template inclui seção de artefatos de fidelidade; (c) caso de borda novo — enforcement de "não-cópia" de protótipo; (d) restrição adicional — protótipo preservado é código *não-produção* e não deve ser importado em `src/`.
>
> **v3 — 2026-08-07 (TDD contextualizado, durante revisão do `validator`).** Durante revisão humana do `validator/SKILL.md` foi apontada uma lacuna: codebases legadas nem sempre suportam TDD ortodoxo. Ajuste aplicado à tese ([v3 do documento base](../../propostas/spec-loop-engineering.md)) e refletido aqui: (a) critério A6 novo — validator suporta os três níveis de TDD (`ortodoxo`, `parcial`, `manual`) com plano de validação manual estruturada e regras anti-fraude; (b) critério C2 ampliado — manifesto ganha campo `tdd-aplicavel`; (c) caso de borda novo — codebase legada onde TDD é inviável; (d) restrição adicional — plano de validação manual precisa ser executável por terceiro e exige evidência anexa em cada passo.

---

## Intenção

Substituir o método ECHO pelo Spec Loop Engineering (SLE): refatorar as três skills atuais em quatro skills novas — uma por papel de agente (Definidor/Designer, Validador, Executor, Observador) — implementando as três invariantes de separação com enforcement determinístico em três camadas, e migrando a identidade do repositório de ECHO para SLE.

## Contexto

Uso continuado das skills atuais confirmou disciplina positiva mas expôs três lacunas: (1) a mesma sessão define, executa e valida — violando o princípio de generator/evaluator separation da literatura de loop engineering (Osmani, jun/2026); (2) enforcement é probabilístico, dependendo de julgamento de modelo/usuário; (3) Fase O não tem estrutura e é a fase mais frágil do método por reconhecimento próprio no README. Tese consolidada em [`propostas/spec-loop-engineering.md`](../../propostas/spec-loop-engineering.md) (2026-08-07). Esta spec é o teste de ácido do método atual: se ele não conduz a própria substituição, o problema é dele.

## Critérios de aceite

### Grupo A — Estrutura de skills

- [ ] **A1.** Existem quatro skills operacionais em `designer/`, `validator/`, `executor/`, `observer/`, cada uma com `SKILL.md` no formato válido do Claude Code / Cursor.
- [ ] **A2.** Cada `SKILL.md` declara explicitamente: papel executado, fases cobertas, invariantes que respeita, e qual skill invoca no próximo passo do ciclo.
- [ ] **A3.** As três skills antigas (`especificar/`, `planejar/`, `homologar/`) foram removidas em commit dedicado com mensagem que referencia o commit de introdução do SLE.
- [ ] **A4.** A skill `designer` foi usada com sucesso pra conduzir esta própria spec — teste de ácido do método atual.
- [ ] **A5.** As três skills afetadas pela fidelidade documentam explicitamente as regras do protótipo preservado (N3): `designer` documenta preservação em `docs/specs/[nome]-prototipo/` com marcação de não-código-de-produção; `validator` documenta acesso ao protótipo apenas durante Fase Traduzir para escrever testes de fidelidade (Camada 3, opcional); `executor` documenta acesso como referência não-copiável de fidelidade visual/UX/comportamental, com Clean Code obrigatório na escrita do zero.
- [ ] **A6.** A skill `validator` documenta explicitamente os três níveis de TDD (`ortodoxo`, `parcial`, `manual`) declarados via campo `tdd-aplicavel` no manifesto. Em `parcial` e `manual`, o Validator escreve plano de validação manual estruturada em `tests/[nome-da-tarefa]/manual-validation.md` com passos que possuem ação concreta, entrada específica e evidência anexável. Fase Homologar exige evidência anexa (log/screenshot/output) para cada passo manual — sem evidência, o passo não conta como executado. Cada item que cai em manual é registrado em `.sle/pressao-metodo.md`.

### Grupo B — Invariantes enforçados

- [ ] **B1.** Cada skill roda em subagente/sessão isolada, sem contexto compartilhado com as outras. Verificação: inspeção do prompt inicial de cada skill declara o isolamento.
- [ ] **B2.** Hooks (Camada 2) bloqueiam: Definidor escrevendo código de produção; Executor escrevendo testes; Validador escrevendo código de produção. Cada hook tem teste próprio que dispara e verifica o bloqueio.
- [ ] **B3.** CI (Camada 3) tem workflow com três checks: spec ↔ test file 1-para-1; cobertura de crítério por tag em teste; PR modificando código sem diff em spec é bloqueado.

### Grupo C — Contratos revisados

- [ ] **C1.** `template-especificacao.md` foi atualizado com: seção "contrato arquitetural" separada da comportamental; gate explícito de falsificabilidade; nota sobre spec enriquecida em N3; **seção "Artefatos de fidelidade (N3)"** que registra caminho do protótipo preservado quando aplicável e lista aspectos visuais/UX/microinteração que exigem preservação.
- [ ] **C2.** Manifesto do repo `echo-skills` foi atualizado com: referência ao padrão de código local; hooks ativos declarados; CI templates declarados; nível de rigor esperado; **campo `tdd-aplicavel` (`ortodoxo` / `parcial` / `manual`) — default `ortodoxo` quando ausente**; domínios ativos revisados (`plataforma` e `integração` passam a ativos).
- [ ] **C3.** Log global `.sle/pressao-metodo.md` foi criado com cabeçalho apropriado, pronto pra receber entradas.
- [ ] **C4.** `dominios.md` mantém corpo intacto, atualiza apenas referências a "método ECHO" para "método SLE".

### Grupo D — Fase O estruturada

- [ ] **D1.** `observer/SKILL.md` cobre A1-A4 com prompts distintos por atividade e explicita A5 (calibração disciplinar) como humana não-delegável.
- [ ] **D2.** `observer/SKILL.md` documenta ambos os modos de disparo (evento e cadência) com pelo menos um exemplo concreto de cada.
- [ ] **D3.** `observer/SKILL.md` proíbe explicitamente propor código, teste, plano ou desenho — restrição auditável no output.

### Grupo E — Migração de identidade

- [ ] **E1.** `README.md` foi reescrito refletindo SLE como método, com seção "vindo do ECHO" documentando as mudanças-chave.
- [ ] **E2.** `metodologia-echo.md` foi renomeado para `metodologia-sle.md` e reescrito com o novo ciclo.
- [ ] **E3.** Todo arquivo em `propostas/`, `dominios.md`, e config do repo (`.echo/`, `.sle/`) atualizou referências a ECHO → SLE mantendo corpo.
- [ ] **E4.** `docs/migracao-echo-sle.md` (novo) documenta equivalências fase-a-fase e o que muda pra usuários da versão anterior.

## Casos de borda considerados

- Usuário roda a skill antiga (`especificar`, `planejar`, `homologar`) durante ou após o período de migração — como é orientado?
- Repositório consumidor atualiza para SLE mas não tem manifesto — comportamento degradado ou bloqueio?
- Hook determinístico (Camada 2) gera falso positivo em código legítimo — mecânica de override existe? como é auditada?
- CI falha porque PR tocou código mas foi refactor puro (mesmo comportamento observável) — a spec precisa ser tocada mesmo assim?
- Skill `designer` termina spec com pergunta pendurada por bug do próprio agente — como se detecta que ela violou a própria regra de fechamento?
- Handoff entre skills numa sessão que o harness não suporta subagentes — degradação para "uma skill de cada vez, sem invocação automática"?
- Autoreferência: a spec do SLE foi escrita em ECHO — isso vira dívida técnica ou fica como marca histórica legítima?
- Protótipo N3 preservado em `docs/specs/[nome]-prototipo/`: como enforçar que o Executor não copie código (só use como referência)? Enforcement determinístico razoável é bloquear import/require do caminho `docs/specs/*/prototipo/**` a partir de `src/` — atrapalha caso legítimo? Auditoria manual como fallback?
- Testes de fidelidade (Camada 3) escritos pelo Validador em N3 podem ficar frágeis (screenshot muda a cada refactor visual sem regressão real). Como sinalizar diferença entre "quebra legítima" e "regressão de fidelidade" sem virar ruído contínuo?
- Codebase legada onde TDD é comprovadamente inviável (framework de teste ausente, acoplamento excessivo, custo de setup maior que valor de captura). Manifesto declara `parcial` ou `manual`; Validator produz plano de validação manual estruturada. Como evitar que "manual" vire válvula de escape que apaga todo enforcement do método? (Mitigação prevista: cada uso registrado em `.sle/pressao-metodo.md`; Fase O detecta padrão persistente e força reflexão sobre modernização.)
- Repositório em `manual` conflita com Camada 3 do enforcement (CI verifica cobertura de crítério por tag em teste). Como Camada 3 lida com repositórios sem testes automatizados — degrada, bloqueia, ou tem check alternativo baseado em `manual-validation.md`?

## Domínios envolvidos

Manifesto atual do `echo-skills` declara zero domínios ativos: *"toda mudança aqui é regra de negócio do próprio método — `miolo`, na classificação do catálogo."* Aplicando a regra da skill `especificar` (usar domínios ativos do manifesto):

| item | classificação |
|---|---|
| Todos os 18 critérios de aceite (A1–E4) | miolo |
| Todos os 7 casos de borda | miolo |

**Nota histórica:** esta refatoração *muda* o manifesto — `plataforma` e `integração` passam a ativos após conclusão. Specs futuras deste repo poderão ter classificações diferentes.

## Fora de escopo

- **Implementação de subagentes específicos de domínio** (segurança-agente, dados-agente etc.). Decomposição interna do papel Executor é decisão de Fase C, não desta spec.
- **Migração retroativa de specs antigas** para o novo template. Só specs criadas após a refatoração seguem o novo formato; specs existentes ficam como estão.
- **Documentação da metodologia em inglês.** Repo continua bilíngue de facto (nomes de pasta em inglês; conteúdo em português). Tradução completa fica pra iteração futura, se algum dia.
- **Publicação/divulgação do método.** SLE nasce dentro do repo pessoal; qualquer publicação depende de validação em pelo menos 3 tarefas reais.
- **Skill `observer` rodando em cadência real** (cron / GitHub Actions scheduled). O *código* da skill entra na spec, mas colocar rodando sozinha em produção diária é próximo passo, não parte desta refatoração.

## Restrições

- Repo continua funcionando em Windows/PowerShell (ambiente do usuário).
- Convenções atuais do repo mantidas: markdown puro para documentação, uma spec por feature em `docs/specs/`, log de pressão em `.sle/` (com alias legado em `.echo/`).
- Todas as skills continuam com conteúdo em português (mesmo com pasta em inglês).
- Compatibilidade com Claude Code é mandatória; compatibilidade com Cursor é desejável — declarar explicitamente onde diverge, se divergir.
- Nenhuma dependência de serviços externos pagos como pré-requisito pra usar SLE.
- **Protótipo N3 preservado é código *não-produção*.** Não deve ser importado em `src/`, não conta em cobertura, não roda em CI de produção. Convive no repositório como referência viva de fidelidade, análogo a fixtures ou mocks — mas dedicado ao ciclo do SLE.
- **Plano de validação manual estruturada (níveis `parcial` e `manual`)** precisa ser executável por terceiro: ação concreta ("execute `curl X`"), entrada específica ("payload `{...}`"), evidência anexável ("response body igual a Y, ou screenshot Z"). Passo mal escrito não conta como cobertura. Fase Homologar exige evidência anexa para cada passo — sem evidência, o passo não conta como executado.

## Ambiente / destino

- **Repositório:** `C:\dock-codes\echo-skills`
- **Branch:** `refatoracao/spec-loop-engineering` (novo, dedicado)
- **Novas pastas na raiz:**
  - `designer/` — skill do Definidor/Designer
  - `validator/` — skill do Validador
  - `executor/` — skill do Executor
  - `observer/` — skill do Observador
  - `tooling/` — hooks templates + CI workflows (visível na raiz, faz parte do repositório conceitualmente)
- **Novo arquivo:** `docs/migracao-echo-sle.md`
- **Diretório de config no repo consumidor:** `.sle/` como padrão novo, `.echo/` como alias legado. Skills leem os dois; preferem `.sle/` se ambos existirem.
- **Arquivos renomeados:** `metodologia-echo.md` → `metodologia-sle.md`.
- **Skills antigas removidas** em commit dedicado que referencia o commit de introdução do SLE (permite `git checkout` para SHA anterior como caminho de reversão).

## Nível de risco

**[x] Difícil de reverter** — muda identidade do repo, adiciona componente executável, refatora skills que já foram usadas em produção pessoal. Cabe todo o rigor de N3.

---

## Alternativas consideradas

**Alternativa 1 — Refatoração pontual, mantendo ECHO.** Adicionar só a Fase O como skill, ou só um verificador independente na Fase H, sem reformar os papéis.  
*Descartada porque:* os três problemas estruturais (anti-teatro, drift, enforcement probabilístico) são a mesma falha em momentos diferentes do ciclo. Nenhuma reforma pontual endereça a raiz, que é a ausência de separação estrutural de papéis. Corrigir um sintoma deixa os outros dois intactos.

**Alternativa 2 — Adoção direta de loop engineering (Osmani/Cherny/Steinberger).** Aceitar a premissa da literatura: agente prompta agente, humano observa métricas de longe.  
*Descartada porque:* contradiz a premissa do método. SLE mantém deliberadamente o humano no meio como *premissa aceleradora*, não como bottleneck removível. A escolha não é "adotar a moda" — é sintetizar peças de loop engineering (separação, verificador independente, harness) dentro de uma tese oposta sobre o papel do humano.

**Alternativa 3 — Fatiamento por domínio como estrutura primária.** Cada domínio (segurança, dados, plataforma) teria seu próprio ciclo E-C-H-O, com papéis próprios.  
*Descartada porque:* overhead massivo em setup; maioria das tarefas mistura domínios; contradiz a leitura já feita em `dominios.md` de que domínio é *endereço de roteamento*, não estrutura de ciclo.

## Dependências e impacto

**Dependências técnicas:**
- Harness (Claude Code, Cursor, ou equivalente) que suporte subagentes com contexto isolado — condição indispensável pra Camada 1 de enforcement.
- Hooks disponíveis no harness com granularidade suficiente pra bloquear operações de arquivo por padrão.
- CI configurável (GitHub Actions, GitLab CI ou equivalente) pra Camada 3.

**Impacto direto:**
- Todo repositório consumidor: manifesto ganha campos novos; specs existentes seguem sendo válidas mas não seguem o novo template.
- `docs/specs/decomposicao-por-dominio.md` (spec V2 existente) fica no formato antigo, tratado como histórico.
- Identidade do repositório: deixa de ser markdown-puro; passa a ter artefatos executáveis em `tooling/`.

**Impacto colateral:**
- Manifesto do `echo-skills` passa a declarar `plataforma` e `integração` como ativos após a conclusão. Specs futuras deste repo poderão ter classificações diferentes.

## Plano de verificação

Além dos testes unitários já cobertos pelos critérios de aceite (cada hook tem teste; cada crítério vira teste ou check estrutural), a verificação inclui:

- **Piloto controlado:** usar a skill `designer` refatorada pra conduzir uma tarefa real *distinta* da própria refatoração — validar que o ciclo de 6 fases funciona end-to-end.
- **Auto-referência (A4):** comprovada pela própria existência desta spec, conduzida com `especificar` atual. Se a Fase E terminar sem quebra estrutural, é evidência forte.
- **Simulação de CI localmente** com `act` (ou equivalente) antes de mergear na main.
- **Piloto em harness alternativo:** rodar `designer` no Cursor após rodar no Claude Code — validar portabilidade, ou documentar divergências no `metodologia-sle.md`.
- **Um ciclo Observer completo** — pelo menos uma volta com evento simulado + uma cadência-driven — antes de declarar a skill `observer` funcional.

## Decisão de reversibilidade

Se a refatoração se mostrar problemática após implementação:

1. **Curto prazo (reversão total):** `git revert` para o commit inicial do SLE. As skills antigas foram removidas em commit dedicado (A3), então elas são recuperáveis pelo histórico com `git checkout` para o SHA anterior.
2. **Médio prazo (reversão parcial):** se o problema for isolado (uma das quatro skills não funciona bem), o método suporta operar híbrido — usar `designer` novo e `homologar` antigo, por exemplo — enquanto se corrige. A documentação de migração precisa prever esse cenário híbrido.
3. **Consumidores externos:** primeira release marcada como *beta*. Uso pessoal por pelo menos 5 tarefas reais antes de sinalizar estável.
4. **Manifesto ganha seção de opt-out:** repos consumidores podem opcionalmente declarar "SLE opt-out" no manifesto, forçando uso das skills antigas enquanto durar a coexistência via alias legado `.echo/`.

## Perguntas em aberto

Incertezas genuínas que só uso real vai responder:

- Ao rodar SLE em 5+ tarefas reais, algum dos três invariantes se mostrará custoso demais? (Ex: separação Designer/Executor pode ser excessiva pra tarefas curtas N2.) O método precisa de exceção para "N2 sem separação"?
- Qual é a granularidade real de hooks que o harness (Claude Code / Cursor) permite hoje, sem gambiarra? Se a limitação for severa, a Camada 2 pode ficar mais fraca que projetada.
- Fase O em cadência-driven — semanal, quinzenal ou mensal? Só uso real revela.
- Anti-teatro: o Validador retornando spec vaga vai virar sinal útil, ou vai virar ruído que o Definidor aprende a evitar sem melhorar a spec? Baseline necessário.
- O agente-Observador, ao propor reconciliação (A3), pode virar oráculo apesar da restrição de output? Se sim, mais salvaguardas podem ser necessárias.
- SLE resolve *simetria* de erros do agente (Definidor, Executor, Validador podem cada um falhar). Mas o humano no Gate 3 pode aprovar por preguiça. Como detectar sem policiar disciplina (que A5 reserva pro humano)?

---

*Spec conduzida via skill `especificar` do método ECHO em 2026-08-07 — teste de ácido do próprio método antes de ele ser substituído. Base intelectual em [`propostas/spec-loop-engineering.md`](../../propostas/spec-loop-engineering.md). Próximo passo: encaminhamento para skill `planejar` (Fase C), que decide sobre fatiabilidade e produz o plano de implementação a ser aprovado antes de qualquer código.*

---

## Histórico de revisões

**v3 — 2026-08-07 (TDD contextualizado durante revisão do `validator`):** identificação, durante revisão humana do `validator/SKILL.md`, de que codebases legadas nem sempre suportam TDD ortodoxo. Skill `validator` reescrita com novo Passo 3.1 (plano de validação manual estruturada) e Passo 8 ampliado (execução manual com evidência anexa). Tese `propostas/spec-loop-engineering.md` promovida a v3. Critérios adicionados: A6, C2 ampliado. Casos de borda adicionados: codebase legada com TDD inviável, tensão entre nível `manual` e Camada 3 de enforcement. Restrição adicional: passo manual precisa ser executável por terceiro com evidência anexável. Manifesto ganha campo `tdd-aplicavel`.

**v2 — 2026-08-07 (ajuste de fidelidade durante Fase C):** identificação, durante a implementação das skills (Passos 2–5 do plano), da lacuna do descarte de protótipo em N3. Skills já commitadas (`designer`, `validator`, `executor`, `observer`) revisadas em conjunto; tese `propostas/spec-loop-engineering.md` promovida a v2. Critérios adicionados: A5, C1 ampliado. Casos de borda adicionados: enforcement de não-cópia de protótipo, fragilidade de testes de fidelidade. Restrição adicional: protótipo preservado é código não-produção. A refatoração continua no mesmo escopo, com esses acréscimos absorvidos.

**v1 — 2026-08-07:** spec original conduzida via `especificar` do ECHO — teste de ácido do próprio método antes da substituição. Protótipo em N3 era descartado após consolidação.
