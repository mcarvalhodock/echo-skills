# Plano de implementação: Refatoração ECHO → SLE

> Referência: spec em [`docs/specs/refatoracao-para-spec-loop-engineering.md`](../specs/refatoracao-para-spec-loop-engineering.md).  
> Aprovado em 2026-08-07.
>
> **v2 — 2026-08-07 (ajuste durante Fase C):** durante a execução dos passos 2–5, foi identificada a *fissura da fidelidade* (protótipo N3 descartado gera frustração contratual). Ajuste aplicado à tese v2, spec v2, e reflete-se aqui: passos 2, 3, 4 ganham revisão de conteúdo (protótipo preservado, testes de fidelidade Camada 3, referência não-copiável); passo 6 (template) ganha adição da seção "Artefatos de fidelidade (N3)". Nenhum passo novo é adicionado; refinamento de passos existentes. Ver [Histórico de revisões](#histórico-de-revisões).
>
> **v3 — 2026-08-07 (TDD contextualizado, durante revisão do `validator`):** durante revisão humana do `validator/SKILL.md` foi identificada a lacuna do TDD em codebases legadas. Ajuste aplicado à tese v3, spec v3, e reflete-se aqui: passo 3 ganha adição de Passo 3.1 (validação manual estruturada) e reescrita do Passo 8; passo 7 (manifesto) ganha campo `tdd-aplicavel`. Mapeamento com critérios ganha A6. Nenhum passo novo; refinamento de escopo.

---

## Fatiabilidade

**Não-fatiável.** Falha em pluralidade (100% miolo conforme manifesto atual) e em independência (grupos altamente acoplados: B depende de A; E depende de tudo; C referencia A e B). Passa em massa, mas duas de três condições reprovam. **Regra da skill "falta uma, não fatia" se aplica.** Plano sai no formato padrão, sem menção a subagente ou sub-specs.

## Passos, em ordem

### Fase 1 — Preparação estrutural

1. Criar pastas: `designer/`, `validator/`, `executor/`, `observer/`, `tooling/`, `tooling/hooks/`, `tooling/ci/`.

### Fase 2 — Skill `designer` (conduz Definir + Desenhar)

2. Escrever `designer/SKILL.md` completo:
   - Frontmatter YAML válido para Claude Code / Cursor
   - Conduta de spec com gate de falsificabilidade explícito
   - Classificação por domínio (mantém lógica atual)
   - Expansão para plano arquitetural com cláusulas
   - Regras do protótipo N3 (só nesse nível, consolidação obrigatória, **preservado como artefato de fidelidade em `docs/specs/[nome]-prototipo/` após consolidação — não descartado**)
   - Handoff estrutural para `validator`, incluindo indicação do caminho do protótipo preservado quando aplicável

### Fase 3 — Skill `validator` (conduz Traduzir + Homologar)

3. Escrever `validator/SKILL.md` completo:
   - Frontmatter YAML
   - Recepção de spec (+ enriquecida, + protótipo preservado quando N3)
   - Escrita de testes em **três** camadas: BDD (comportamento) + contrato (arquitetural) + **fidelidade (Camada 3, opcional, apenas em N3 quando aspectos visuais/UX/microinteração emergiram — tags `@fidelidade:visual`, `@fidelidade:ux`, `@fidelidade:microinteracao`)**
   - **TDD contextualizado** (v3): três níveis declarados no manifesto via campo `tdd-aplicavel` (`ortodoxo` / `parcial` / `manual`). Em `parcial` e `manual`, Validator escreve **plano de validação manual estruturada** em `tests/[nome-da-tarefa]/manual-validation.md` com passos que possuem ação concreta, entrada específica, evidência anexável. Fase Homologar exige evidência anexa (log/screenshot/output) para cada passo manual.
   - **Acesso ao protótipo preservado apenas durante Fase Traduzir** para escrever testes de fidelidade — na Fase Homologar (nova sessão), esse contexto não é carregado
   - Poder de retorno estrutural de spec vaga
   - Handoff de suite (+ plano manual quando aplicável) para `executor`
   - Retorno posterior para rodar testes automatizados + executar plano manual contra código do Executor
   - Reporte de evidência (com evidência anexa para cada passo manual)
   - Preparação de checklist para Gate 3 (revisão arquitetural humana)

### Fase 4 — Skill `executor` (conduz Implementar)

4. Escrever `executor/SKILL.md` completo:
   - Frontmatter YAML
   - Leitura de spec + plano + testes falhando + **protótipo preservado quando N3, como referência de fidelidade visual/UX/comportamental**
   - **Proibição explícita de copiar código do protótipo** — implementação é do zero, seguindo Clean Code; a fidelidade é preservada como *observável* (verificado pelos testes de fidelidade da Camada 3)
   - Leitura de padrão Clean Code do manifesto
   - Implementação até testes passarem
   - Proibição explícita de escrever ou modificar testes
   - Handoff de volta para `validator` (Homologar)

### Fase 5 — Skill `observer` (conduz Observar)

5. Escrever `observer/SKILL.md` completo:
   - Frontmatter YAML
   - Detecção de modo (evento-driven / cadência-driven)
   - A1 (discovery), A2 (análise), A3 (proposta de reconciliação), A4 (extração de padrão) com prompts distintos
   - Declaração explícita: A5 (calibração disciplinar) é humana não-delegável
   - Escrita em dois logs: (b) por spec, (c) `.sle/pressao-metodo.md`
   - Restrição rigorosa de output: não propor código, teste, plano ou desenho

### Fase 6 — Atualização de contratos

6. Atualizar `template-especificacao.md`:
   - Adicionar seção "Contrato arquitetural" em N2 e N3
   - Adicionar gate de falsificabilidade explícito
   - Adicionar nota sobre spec enriquecida em N3
   - **Adicionar seção "Artefatos de fidelidade (N3)"** — registra caminho do protótipo preservado quando aplicável e lista aspectos visuais/UX/microinteração que exigem preservação (base para o Validator escrever testes de fidelidade Camada 3)
   - Substituir referências ECHO → SLE

7. Criar `.sle/manifesto.md` com campos novos:
   - Domínios ativos (revisados: `plataforma` e `integração` passam a ativos)
   - Ferramental disponível
   - Padrão de código local
   - Hooks ativos declarados
   - CI templates declarados
   - Nível de rigor esperado
   - **`tdd-aplicavel`** (novo, v3): `ortodoxo` (default) | `parcial` | `manual`. Declara viabilidade de TDD ortodoxo no repositório; `parcial` e `manual` habilitam plano de validação manual estruturada no Validator.
   
   Manter `.echo/manifesto.md` com nota de redirect textual explícita para `.sle/manifesto.md`.

8. Criar `.sle/pressao-metodo.md` com cabeçalho apropriado, análogo ao `pressao-catalogo.md` atual mas para aprendizados sistêmicos que apontam pra ajustar o próprio método.

9. Atualizar `dominios.md`: apenas referências textuais ECHO → SLE, corpo intacto.

### Fase 7 — Enforcement determinístico

10. Criar hooks em `tooling/hooks/`:
    - `block-designer-writing-code/` (implementação em Python + docs em md)
    - `block-executor-writing-tests/`
    - `block-validator-writing-code/`
    - `README.md` explicando como cada hook é ativado no harness (Claude Code, Cursor)

11. Escrever testes unitários dos hooks em `tooling/hooks/tests/`. Cada hook tem pelo menos: teste que confirma bloqueio; teste que confirma não-interferência em operações permitidas.

12. Criar CI workflows em `tooling/ci/`:
    - `spec-test-parity.yml` — verifica que toda spec tem test file correspondente
    - `criterion-coverage.yml` — verifica cobertura de crítério por tag em teste
    - `pr-spec-diff.yml` — bloqueia PR modificando código sem diff em spec
    - `README.md` explicando adaptação por repositório

13. Testar CI localmente com `act` (ou equivalente disponível no ambiente Windows). Documentar resultado (mesmo se ferramenta local não funcionar, o CI real vai rodar no primeiro PR).

### Fase 8 — Migração de identidade

14. Reescrever `README.md`:
    - Substituir ECHO por SLE mantendo intenção pedagógica
    - Descrever ciclo em 6 fases
    - Descrever 4 papéis
    - Descrever enforcement em 3 camadas
    - Seção "vindo do ECHO" com as mudanças-chave

15. Renomear `metodologia-echo.md` → `metodologia-sle.md` e reescrever conteúdo com:
    - Novo ciclo
    - Papéis e invariantes
    - Enforcement
    - Contratos de visibilidade

16. Atualizar `propostas/expansao-para-times.md`:
    - Nota de rodapé indicando SLE mudou o baseline
    - Alguns eixos podem precisar revisão (mas essa revisão não é escopo desta refatoração)

17. Criar `docs/migracao-echo-sle.md` completo:
    - Equivalências fase-a-fase
    - Como usuários da versão antiga se orientam
    - Onde as skills novas ficam (que era responsabilidade das antigas)

### Fase 9 — Remoção controlada das skills antigas

18. Auditoria via `rg 'ECHO|especificar|planejar|homologar'` (com exclusão explícita dos arquivos que documentam migração): confirmar que nenhuma referência ativa ficou pra trás. Cada match precisa ser resolvido explicitamente.

19. Remover pastas `especificar/`, `planejar/`, `homologar/` em commit dedicado. Mensagem do commit referencia o SHA do primeiro commit do SLE (Fase 2) e explica caminho de reversão via `git checkout`.

## Arquivos afetados

**Criar (10 caminhos):**
- `designer/SKILL.md`
- `validator/SKILL.md`
- `executor/SKILL.md`
- `observer/SKILL.md`
- `tooling/hooks/*` (3 hooks × 2 arquivos = 6 arquivos + README + tests)
- `tooling/ci/*` (3 workflows + README)
- `.sle/manifesto.md`
- `.sle/pressao-metodo.md`
- `metodologia-sle.md` (via rename de `metodologia-echo.md`)
- `docs/migracao-echo-sle.md`

**Modificar (5 caminhos):**
- `template-especificacao.md`
- `README.md`
- `dominios.md`
- `.echo/manifesto.md` (nota de redirect)
- `propostas/expansao-para-times.md`

**Deletar (3 pastas, em commit dedicado da Fase 9):**
- `especificar/`
- `planejar/`
- `homologar/`

## Mapeamento com os critérios de aceite

- **A1** → passos 1–5
- **A2** → passos 2–5 (estrutura obrigatória em cada SKILL.md)
- **A3** → passo 19
- **A4** → pré-atendido pela existência da spec, validado pela ausência de retrabalho durante Fases 2–9
- **A5** (v2) → passos 2, 3, 4 (regras de acesso ao protótipo preservado nas três skills afetadas)
- **A6** (v3) → passo 3 (TDD contextualizado no `validator` com plano de validação manual estruturada)
- **B1** → passos 2–5 (declaração explícita de isolamento em cada SKILL.md)
- **B2** → passos 10–11
- **B3** → passos 12–13
- **C1** → passo 6 (com adição da seção "Artefatos de fidelidade (N3)" em v2)
- **C2** → passo 7 (com adição do campo `tdd-aplicavel` em v3)
- **C3** → passo 8
- **C4** → passo 9
- **D1** → passo 5
- **D2** → passo 5
- **D3** → passo 5
- **E1** → passo 14
- **E2** → passo 15
- **E3** → passos 9, 16, e auditoria no passo 18
- **E4** → passo 17

Todos os 20 critérios têm cobertura explícita. Nenhum critério órfão.

## Ordem de execução e dependências

- **Fase 1** é pré-requisito estrutural pra **Fases 2–5**.
- **Fases 2–5** teoricamente poderiam rodar em paralelo, mas o critério A2 exige que cada `SKILL.md` declare "qual skill invoca no próximo passo". Portanto, ordem *Designer → Validator → Executor → Observer* espelha o fluxo do ciclo e evita retrabalho de referências cruzadas.
- **Fase 6** depende de que os 4 SKILL.md existam (referenciados no template atualizado).
- **Fase 7** depende de **Fase 6** (manifesto declara hooks e CI ativos).
- **Fase 8** depende de **Fases 2–7** (README precisa descrever método completo).
- **Fase 9** depende de **Fase 8** (referências antigas eliminadas antes de deletar arquivos originais).

## Riscos identificados neste plano

**R1 — Limite de granularidade dos hooks do harness.**  
Camada 2 pressupõe hooks capazes de bloquear escrita em paths específicos por identidade do agente. Se Claude Code / Cursor não expuser essa granularidade, o passo 10 vira degradação: hooks viram advertências não-bloqueantes + reforço via CI (Camada 3). Sinal de alerta durante Fase 7: se a documentação do harness não permitir bloqueio por identidade, sinalizo e ajustamos.

**R2 — Ordem de skills gera chicken-and-egg na auto-referência (A4).**  
Se, ao escrever `designer/SKILL.md` (passo 2), for detectado que o método atual não deveria ter conseguido produzir esta spec (algum critério ficou frouxo, algo passou batido), A4 fica sob suspeita. Mitigação: reservar tempo no início do passo 2 pra auditar a spec pela lente do designer refatorado *antes* de escrever seu SKILL.md. Se inconsistências surgirem, voltar à Fase E.

**R3 — Ambiente Windows/PowerShell nos hooks.**  
Hooks precisam funcionar em Windows/PowerShell (restrição da spec) e também em ambientes Unix (portabilidade). Estratégia: implementar em Python (multiplataforma) por padrão; oferecer versões `.sh` e `.ps1` como convenience. Passo 10 assume isso; se se mostrar caro, revisitar.

**R4 — Migração de nomenclatura toca em muitos arquivos.**  
Risco de esquecer referências a "ECHO" em algum arquivo. Mitigação: auditoria via `rg 'ECHO|echo-skills'` no passo 18 antes de considerar Fase 8 concluída. Cada match precisa ser resolvido explicitamente.

**R5 — CI local não-testável no Windows.**  
`act` (simulador GitHub Actions) tem suporte parcial no Windows. Se falhar, passo 13 vira "documentar CI em texto + rodar num primeiro PR real de teste". Não bloqueante, mas menos rigoroso.

**R6 — `.echo/` vs `.sle/` durante a transição.**  
Manter `.echo/manifesto.md` como redirect e criar `.sle/manifesto.md` como principal cria dupla fonte. Mitigação: a nota de redirect em `.echo/manifesto.md` precisa apontar textualmente pra `.sle/manifesto.md` e explicar o alias legado.

## Fora deste plano

- **Piloto em tarefa distinta usando `designer` refatorada** (parte do Plano de Verificação da spec) — fica pra ciclo posterior, depois de mergear.
- **Piloto em harness alternativo (Cursor)** — fica pra depois de validar em Claude Code.
- **Publicação/divulgação do método** — fora de escopo da spec, portanto fora deste plano.
- **Migração retroativa de specs antigas** — fora de escopo da spec.
- **Refactor de `docs/specs/decomposicao-por-dominio.md`** — permanece no formato antigo como histórico.
- **Ativação real da skill `observer` em modo cadência** (cron / scheduled workflow) — só o código da skill entra; ativação em produção é passo seguinte.
- **Ajuste de `.gitignore` para `.sle/`** — decisão operacional pequena; resolvo durante execução se necessário sem replanejar.

---

*Plano gerado pela skill `planejar` do método ECHO em 2026-08-07 — parte do próprio ciclo que este plano vai substituir. A execução segue estritamente a ordem acima; desvios exigem nova aprovação, não improviso silencioso.*

---

## Histórico de revisões

**v3 — 2026-08-07 (TDD contextualizado, durante revisão do `validator`):** durante revisão humana do `validator/SKILL.md` foi apontada lacuna do TDD ortodoxo em codebases legadas. Ajuste aprovado explicitamente (não desvio silencioso). Passo 3 foi reescrito para incluir Passo 3.1 (plano de validação manual estruturada) e Passo 8 ampliado (execução manual com evidência anexa). Passo 7 (manifesto) ganhou campo `tdd-aplicavel`. Mapeamento com critérios ganhou A6.

**v2 — 2026-08-07 (ajuste durante Fase C):** durante execução dos passos 2–5, foi identificada a *fissura da fidelidade* (protótipo N3 descartado apaga aspectos visuais/UX/microinteração verificados). Ajuste aprovado explicitamente pelo humano (não desvio silencioso — obedeceu ao Passo 4 da `planejar`). Passos 2, 3, 4 foram revisados retroativamente para acomodar protótipo preservado + testes de fidelidade (Camada 3) + acesso não-copiável. Passo 6 ganhou adição de "Artefatos de fidelidade (N3)" no template. Nenhum passo novo; refinamento de escopo dentro dos existentes. Mapeamento com critérios ganhou A5. Skills já commitadas (`designer`, `validator`, `executor`) foram reescritas em conjunto para refletir v2.

**v1 — 2026-08-07:** plano original aprovado. Protótipo N3 seria descartado após consolidação; skills não previam Camada 3 de testes de fidelidade nem acesso do Executor a protótipo.
