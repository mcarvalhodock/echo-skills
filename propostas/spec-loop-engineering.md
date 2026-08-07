# Proposta: Spec Loop Engineering — o próximo desenho do método

> **Status: tese consolidada — v2 (ajuste de fidelidade em 2026-08-07).**  
> **v1 (2026-08-07):** tese original consolidada em sessão de design.  
> **v2 (2026-08-07):** ajuste no tratamento do protótipo em N3 — de "descartado após consolidação" para "preservado como artefato de fidelidade". Motivo: durante a Fase C da própria refatoração, foi identificada a *fissura da fidelidade* — protótipo descartado perde informação verificada (aspectos visuais, de UX, microinteração), gerando frustração contratual entre o que foi homologado e o que foi implementado. Ver [Histórico de revisões](#histórico-de-revisões) no fim deste documento.
>
> Este documento é o output de uma sessão de design que sustenta a próxima refatoração do repositório. Não é ainda uma spec — é a base sobre a qual a spec vai ser escrita, aplicando o próprio método ECHO atual antes de ele ser substituído. Se ECHO não sobrevive a especificar a própria substituição, o problema é dele.

---

## Por que este documento existe, e por que aqui

Depois de uso continuado das três skills (`especificar`, `planejar`, `homologar`), duas coisas ficaram nítidas:

1. **A disciplina funciona.** Encontrei precisão no que estava desenvolvendo, e fiz com que o agente de código também encontrasse essa precisão. Isso é o resultado que o método prometia.
2. **A estrutura atual tem o formato do que a literatura mais recente chama de *loop engineering*** — a disciplina de desenhar sistemas que orquestram agentes de IA em ciclos autoverificáveis, cunhada em junho de 2026 por Addy Osmani a partir de falas de Peter Steinberger e Boris Cherny.

Reconhecer o parentesco não é dizer "somos a mesma coisa". ECHO chegou às peças de loop engineering por dentro, mas com uma premissa **oposta** em um ponto crítico: loop engineering quer *remover o humano do posto de quem prompt*a agentes; ECHO quer *manter o humano deliberadamente no meio*, em gates estruturais. Essa diferença de premissa não é semântica — decide toda a arquitetura da refatoração.

Este documento vive em `propostas/` porque ainda não é mudança executada, mas é diferente do `expansao-para-times.md` que também vive aqui: aquele é hipótese não validada; este é tese consolidada, com intenção declarada de virar spec e implementação.

---

## A tese em uma frase

**Spec Loop Engineering (SLE) é ECHO reorganizado sob quatro papéis de agente estruturalmente separados, com o humano como árbitro em três gates críticos, e com enforcement determinístico substituindo enforcement probabilístico onde for possível.**

O nome antigo (ECHO) se aposenta. A nomenclatura vem da síntese de cinco disciplinas: **Spec-Driven Development, Behavior-Driven Development, Test-Driven Development, Loop Engineering e Clean Code (contextualizado)**.

---

## O princípio fundacional

> O humano é premissa aceleradora, não passiva. Ele define, ele aprova, ele julga arquitetura. O agente é executor superior — mas com restrição estrutural, não confiança:
>
> - **Nunca um agente valida o que implementou.**
> - **Nunca um agente implementa o que desenhou.**
>
> O humano fica no meio como árbitro das decisões que o agente não deveria tomar sozinho.

Isso é a formulação, em uma frase, das três invariantes que sustentam toda a arquitetura.

---

## Os cinco pilares intelectuais

Cada um governa uma dimensão distinta do método. Nenhum é acessório.

| Pilar | O que contribui | Onde governa |
|---|---|---|
| **SDD** (Spec-Driven Development) | O **contrato** — nada existe sem spec. Fonte única da verdade. | Fase Definir |
| **BDD** (Behavior-Driven Development) | A **forma** dos critérios — comportamento observável, não implementação. | Definir → Traduzir |
| **TDD** (Test-Driven Development) | A **ordenação** — teste precede código. Executor recebe testes falhando. | Traduzir → Implementar |
| **Loop Engineering** | A **separação de papéis** com invariantes estruturais. | Toda transição entre fases |
| **Clean Code (contextualizado)** | A **qualidade do código** que sobrevive à leitura de outros humanos e agentes futuros, calibrada ao contexto do sistema. | Fase Implementar |

A síntese: **contrato SDD é escrito em linguagem BDD, traduzido em testes TDD por agente independente, executado por outro agente que codifica com padrão Clean Code do repositório — e o humano é árbitro nas três transições que decidem qualidade.**

---

## Os quatro papéis, seus limites

| Papel | Faz | Não faz |
|---|---|---|
| **Definidor / Designer** (agente) | Conduz spec, plano, protótipo (só N3), consolidação | Nunca implementa código de produção |
| **Validador** (agente independente) | Escreve testes a partir da spec, roda testes, reporta evidência | Nunca vê plano, protótipo ou código do Executor antes de rodar |
| **Executor** (agente independente) | Implementa contra spec + testes + plano, seguindo Clean Code do repositório | Nunca escreve teste, nunca homologa |
| **Observador** (agente novo) | Discovery de sinal, análise, proposta de reconciliação de spec, extração de padrão | Nunca propõe código, teste, plano ou desenho |

**Humano** é o quinto agente do sistema, e o único que decide: aprova spec, aprova plano/desenho, responde revisão arquitetural, e calibra disciplina pessoal — atividade que **jamais** é terceirizada ao agente.

### As três invariantes estruturais

1. **Designer ≠ Executor** — quem desenhou não implementa.
2. **Executor ≠ Validador** — quem escreveu não homologa.
3. **Nenhum agente é Árbitro** — decisão sobre contrato, plano e arquitetura tem dono humano nomeado, sempre.

Uma quarta invariante decorre dos três anteriores: **Observador é papel independente**. Se ele for reutilização de Definidor, Executor ou Validador, ele defenderia as próprias decisões ao observar, violando o espírito das três primeiras invariantes.

---

## O ciclo em seis fases

```
1. DEFINIR                    → Definidor + humano
   (spec com critérios BDD, classificação por domínio)
   ▼ GATE HUMANO 1: contrato aprovado

2. DESENHAR                   → Definidor + humano  ← fase expandida
   (plano com cláusulas arquiteturais; protótipo se N3;
    consolidação obrigatória se prototipou → spec enriquecida)
   ▼ GATE HUMANO 2: desenho aprovado

3. TRADUZIR EM TESTES         → Validador (independente)
   (critérios BDD viram testes executáveis; suite falha porque não há código)
   ▼ Handoff estrutural

4. IMPLEMENTAR                → Executor (independente do Validador)
   (recebe spec + plano + testes falhando; codifica até passar,
    seguindo Clean Code declarado no manifesto)
   ▼ Handoff estrutural

5. HOMOLOGAR                  → Validador (o mesmo do passo 3)
   (roda os testes que ele escreveu; reporta evidência real)
   ▼ GATE HUMANO 3: revisão arquitetural

6. OBSERVAR                   → Observador + humano
   (discovery, análise, reconciliação de spec, extração de padrão)
   ▼ volta pra 1 (com spec atualizada)
```

Comparado com E-C-H-O atual (quatro fases), o ciclo do SLE tem seis. A expansão vem de duas separações estruturais: **Desenhar** vira fase própria (antes embutida em `planejar`); **Traduzir em testes** vira fase própria (antes embutida em `homologar`, e feita *depois* da implementação, não antes).

---

## Regras do protótipo (só Nível 3)

- **Só existe em N3.** Nível 2 tem plano com cláusulas arquiteturais explícitas, mas não código exploratório.
- **Consolidação obrigatória.** Se o Designer prototipou, é obrigado a extrair o aprendizado: decisões de comportamento vão pra **spec enriquecida** (que substitui a spec original como referência ativa, com marcador histórico); cláusulas arquiteturais vão pro plano.
- **Preservado como artefato de fidelidade após consolidação.** O protótipo é movido para `docs/specs/[nome]-prototipo/` e marcado explicitamente como *não-código-de-produção*. Ele **não vira código de produção**, mas **também não é descartado** — permanece disponível como referência de fidelidade visual, de UX e de microinteração.
- **Acesso ao protótipo por papel:**
  - **Executor** o usa como referência de fidelidade durante a implementação. **Não copia código dele** — escreve do zero seguindo Clean Code. Mas o resultado precisa preservar comportamento observável, visual e experiência.
  - **Validator** o usa apenas durante a Fase Traduzir para escrever testes de fidelidade (Camada 3, ver adiante) quando aspectos visuais/UX emergiram. **Não vê o protótipo na Fase Homologar** — a integridade da homologação exige contexto isolado.
  - **Designer** o mantém como registro do próprio aprendizado; pode revisitá-lo em iterações futuras.
- **Clean Code relaxado no protótipo.** É código exploratório, não código de produção — nem a consolidação nem a preservação mudam isso. Executor não deve copiar (o código do protótipo não segue Clean Code do repositório).

O objetivo dessa rigidez é preservar o invariante 1 (Designer ≠ Executor) mesmo quando o Designer produz código durante a fase de desenho — **e** preservar precisão da fidelidade sem terceirizar ao julgamento do Executor.

### Por que "preservar" e não "descartar"

A tese v1 previa descarte após consolidação, sob o argumento de que "aprendizado explícito é capturado na spec enriquecida; o resto é implícito e não deveria atravessar." A tese v2 corrige essa premissa:

**"Aprendizado explícito é capturado" só funciona se o Designer conseguir *nomear* cada aspecto que vale preservar.** Aspectos visuais e de UX resistem a essa nomeação — não porque sejam inefáveis, mas porque nomeá-los depende de vocabulário que só emerge *depois* da experiência do protótipo. Sob pressão de consolidação, o Designer captura o que sabe nomear e perde o resto.

Descartar o protótipo depois disso não é limpeza — é apagar evidência verificada. A frustração contratual resultante (código passa nos testes mas "não é aquilo que a gente aprovou") é o preço concreto da rigidez em v1.

A preservação em v2 preserva a informação sem quebrar o invariante 1: o protótipo continua sendo *referência*, não *código-base*. Executor escreve do zero. Testes de fidelidade escritos pelo Validator verificam que a escrita do zero preservou o que precisava ser preservado.

---

## Contrato de visibilidade entre agentes

O que cada papel enxerga define se "independência" é estrutural ou só declarada.

| Artefato | Definidor | Validador | Executor | Observador | Humano |
|---|---|---|---|---|---|
| Spec original | escreve | ✅ | ✅ | ✅ | ✅ |
| Spec enriquecida (N3) | escreve | ✅ | ✅ | ✅ | ✅ |
| Plano (com cláusulas arquiteturais) | escreve | ❌ | ✅ | ✅ | ✅ |
| Protótipo (antes da consolidação) | escreve | ❌ | ❌ | ✅ (histórico) | ✅ |
| Protótipo N3 preservado (após consolidação) | ✅ (registro) | ✅ **só na Fase Traduzir** | ✅ (referência, não copia) | ✅ | ✅ |
| Suite de testes (código completo) | ❌ | escreve | ✅ | ✅ | ✅ |
| Testes de fidelidade (Camada 3, N3) | ❌ | escreve **na Fase Traduzir** | ✅ | ✅ | ✅ |
| Código do Executor (antes de rodar teste) | ❌ | ❌ | escreve | ✅ | ✅ |
| Resultado de execução | ❌ | ✅ | ❌ | ✅ | ✅ |

**Quatro firewalls estruturais** (não retóricos):

- **Validador nunca vê o plano.** Cláusulas arquiteturais moram na spec (não só no plano) porque o Validador precisa poder escrever testes de contrato sem ter acesso ao plano. Consequência: a spec ganha uma seção de contrato arquitetural além da seção comportamental.
- **Validador nunca vê o código do Executor antes de rodar os testes.** Se ele lê o código, pode ajustar teste pra passar. Operação em dois momentos: (1) escreve testes contra spec, submete; (2) recebe artefato do Executor, roda, reporta.
- **Validador vê o protótipo (N3) apenas na Fase Traduzir.** Acesso é específico à escrita de testes de fidelidade. Ao entrar em Fase Homologar (nova sessão), o Validador **não** carrega esse contexto — mantém isolamento de execução.
- **Executor vê testes completos (TDD clássico) + protótipo N3 como referência não-copiável.** Ele sabe exatamente o que precisa passar. Overfitting e cópia de protótipo são riscos reconhecidos; a mitigação vem da qualidade da spec, da revisão arquitetural, e dos testes de fidelidade que verificam preservação sem exigir cópia.

## Testes de fidelidade (Camada 3, N3 opcional)

Além de testes BDD (comportamento) e testes de contrato (cláusulas arquiteturais), o Validator escreve **testes de fidelidade** em N3 com protótipo preservado, quando aspectos visuais/UX/microinteração emergiram da consolidação.

Exemplos por framework:
- **Visual:** screenshot tests, snapshot tests de DOM.
- **UX:** interaction tests (Playwright, Cypress) que reproduzem fluxos observados no protótipo.
- **Microinteração:** testes de timing, ordem de eventos, feedback ao usuário.

**Regras:**
- **Opcional, não obrigatório.** Escreva **apenas** quando o aspecto realmente merece verificação mecânica. Teste de fidelidade escrito por completude vira suite frágil.
- **Tags específicas:** `@fidelidade:visual`, `@fidelidade:ux`, `@fidelidade:microinteracao`.
- **Cobrem preservação, não igualdade lexical.** O Executor não precisa produzir o mesmo código; precisa produzir o mesmo *observável*.
- **Falham em silêncio se irrelevantes.** Se a consolidação capturou tudo em BDD/contrato e não sobrou aspecto visual/UX pra cobrir, essa camada simplesmente não é escrita.

---

## Anti-inchamento da spec

O risco central de "cláusulas arquiteturais moram na spec" (decisão A da visibilidade) é a spec inchar com o tempo e perder relação sinal/ruído. Três mecânicas atacam três forças distintas:

- **M1 — Uma spec por feature, não por sistema.** Já é prática implícita; vira regra dura. Heurística de fecho: *se você não consegue explicar a spec inteira em 5 minutos, ela virou spec de sistema — fatie*.
- **M4 — Seções tipadas com regras próprias de crescimento.**
  - Intenção: 1 frase, quase-imutável. Nova iteração = nova spec.
  - Critérios BDD: aditivo, com checklist de sobreposição a cada novo.
  - Contrato arquitetural (só N3, consolidado): aditivo, mas cada cláusula precisa ser referenciada por pelo menos um teste. Cláusula órfã sai.
  - Casos de borda: aditivo, com reconciliação obrigatória em Fase O.
  - Fora de escopo: aditivo, imutável (só cresce, nunca encolhe).
  - Restrições: aditivo, mas datadas e justificadas.
- **M6 — Fase O reconcilia, não só soma.** Toda modificação de spec passa por reconciliação ativa: se a nova cláusula contradiz uma existente, uma das duas sai. Não empilha.

O que **não** entra: limite arbitrário de tamanho, rotação obrigatória por tempo, manifesto de contratos separado da spec.

---

## Fase O expandida

Fase O deixa de ser retrospectiva humana amorfa e ganha estrutura. Cinco atividades, com natureza diferente:

| Atividade | Natureza | Papel |
|---|---|---|
| **A1 — Discovery de sinal** (erro em prod, bug, incidente, teste flaky, PR quebrou) | Mecânica | Agente-Observador |
| **A2 — Análise do sinal** (é bug de código? spec vaga? escopo mal-desenhado?) | Mecânica + julgamento | Agente propõe classificação, humano confirma |
| **A3 — Reconciliação de spec (M6)** (soma? substitui? contradiz?) | Julgamento arquitetural | Agente propõe diff, humano decide |
| **A4 — Extração de padrão** (o que se repete ao longo do tempo?) | Meta-observação | Agente agrega, humano decide se vira mudança de método |
| **A5 — Calibração disciplinar pessoal** (*"quantas vezes pulei o método essa semana?"*) | Auto-observação disciplinar | **Humano exclusivo** — nunca terceirizado |

**Modos de disparo:** ambos.
- **Evento-driven** — sinal chega, Fase O ativa.
- **Cadência-driven** — semanal/mensal, executa em rotina.

**Dois logs, com clientes diferentes:**
- **(b) Log de aprendizado por spec** — fica com a spec; histórico do que foi observado, mesmo depois de reconciliado.
- **(c) Log global do método** — `.echo/pressao-metodo.md` (análogo ao `pressao-catalogo.md` atual, mas para aprendizados sistêmicos). Alimenta a evolução do SLE.

**Mitigação do risco de oráculo:** o Observador tem output rigidamente estruturado. Pode propor reconciliação de spec (A3) e agregar padrão (A4), **não pode** propor código, teste, plano ou desenho. Se derramar em ação, violou papel.

---

## Enforcement determinístico como sistema

O reconhecimento honesto: método atual depende de julgamento do modelo e do usuário pra não ser burlado. Isso é enforcement probabilístico. Três problemas decorrem — e são o mesmo problema em momentos diferentes:

| Problema | Onde falha | Como o SLE ataca |
|---|---|---|
| **Anti-teatro** | Início (spec fake precise) | Falsificabilidade obrigatória + Validador com poder estrutural de retorno |
| **Drift spec/código** | Fim (código evolui, spec fica) | Modificação de código exige atualização de spec (bloqueio de PR) |
| **Enforcement (raiz)** | Qualquer momento | Três camadas cascatadas de harness executável |

### As três camadas de enforcement, cascatadas

**Camada 1 — Handoff estrutural (setup).** Cada papel é agente separado com contexto separado. Enforcement natural do arranjo: o Validador *fisicamente não tem* o código do Executor; o Executor *fisicamente não tem* a implementação dos testes até receber como handoff formal. Custo baixo.

**Camada 2 — Hook determinístico (agente-lifecycle).** Regras que não podem depender de julgamento viram bloqueios no ciclo de vida do agente:
- Executor tentando escrever em `src/` sem spec ativa referenciada → bloqueia.
- Validador tentando ler `src/` antes de escrever testes → bloqueia.
- Definidor tentando escrever em `src/` → bloqueia (invariante 1).
- Modificação de teste depois de entregue → exige justificativa formal.

Custo médio, específico do harness.

**Camada 3 — CI/pipeline (repositório-level).** Regras que sobrevivem ao encerramento da sessão de agente:
- Toda spec em `docs/specs/*.md` tem test file correspondente.
- Cobertura de critério: cada cláusula tem tag correspondente em pelo menos um teste.
- PR com diff em `src/` sem diff em `docs/specs/` → bloqueia.
- Linter/formatter (Clean Code mecânico) passa.

Custo alto, mas o único que sobrevive fora do agente.

**As três cascatam, não competem.** Camada 1 é padrão de execução; Camada 2 é guarda-corpo do agente; Camada 3 é rede de segurança do repositório.

### Como o enforcement resolve anti-teatro e drift, concretamente

**Anti-teatro:**
- Skill `especificar` fecha com gate explícito de *falsificabilidade obrigatória*. Cláusula que "sempre passa" é rejeitada mecanicamente.
- Se o Validador não consegue derivar teste de uma cláusula (ambiguidade real), *devolve a spec sem escrever teste*. Bloqueio de fluxo, não opção. Ciclo volta pra Definir.
- Padrão persistente ("Definidor X faz spec devolvida 4 vezes por semana") vira sinal pra Fase O — A4 (agente propõe refino de template) e A5 (humano calibra disciplina).

**Drift spec/código:**
- Camada 3 direta: PR bloqueia se modifica `src/` sem `docs/specs/`.
- Cláusulas arquiteturais na spec (decisão A) viram testes de contrato pelo Validador — drift comportamental E arquitetural viram testes falhando em CI.
- Único drift que escapa é o semântico (comportamento preservado, intenção mudou). Esse cai na Fase O — auditoria periódica do Observador no modo cadência-driven.

---

## Manifesto do repositório, expandido

O `.echo/manifesto.md` atual declara domínios ativos e ferramental. No SLE, ele ganha responsabilidade adicional:

- Domínios ativos e obrigatórios (mantido)
- Ferramental disponível (mantido)
- **Padrão de código local** (novo) — referência ao STYLE.md, `.cursor/rules/`, linter config, ou similares. Se não declarado, método usa "boas práticas gerais" avisando uma vez. Degrada, não bloqueia.
- **Hooks ativos** (novo) — quais hooks da Camada 2 estão configurados
- **CI templates ativos** (novo) — quais checks da Camada 3 rodam
- **Nível de rigor esperado** (novo) — protótipo, MVP, produção crítica; cada tem baseline diferente pra Clean Code e pra rigor de spec

O manifesto continua sendo declaração, não pendência. Ausência degrada, não bloqueia — mesma lógica do manifesto atual.

---

## Catálogo de domínios: sobrevive intacto

`dominios.md` não muda de estrutura. Muda o *onde* opera no ciclo:

| Fase | Uso do catálogo |
|---|---|
| Definir | Cada critério/caso de borda classificado por domínio |
| Desenhar | Fatiabilidade avaliada; se fatiável, sub-plano por domínio |
| Traduzir | Validador agrupa testes por domínio quando aplicável |
| Implementar | Cada fatia pode virar sub-agente-Executor especializado por domínio (decomposição *dentro* do Executor, não violação) |
| Homologar | Mapeamento crítério ↔ teste ↔ domínio permanece rastreável |
| Observar | Aprendizados categorizados por domínio; pressão sobre catálogo permanece mensurável |

O log `.echo/pressao-catalogo.md` sobrevive como está.

---

## Consequências práticas: o repositório muda de natureza

Aceitar SLE completo significa aceitar que `echo-skills` deixe de ser 100% markdown:

- **Novos artefatos executáveis**: templates de hooks (Claude Code, Cursor), configs de subagentes, CI workflows (GitHub Actions ou equivalente).
- **Manifesto ganha peso**: deixa de ser declaração de contexto e vira quase configuração operacional.
- **Nova pasta possível**: `tooling/` com hooks, actions, subagent configs prontos pra usar em repos consumidores.
- **Migração de identidade**: `README.md`, `metodologia-echo.md`, `template-especificacao.md`, `dominios.md`, `.echo/manifesto.md`, `propostas/expansao-para-times.md` — todos mencionam ECHO. A refatoração inclui migração de nomenclatura como escopo, não como bikeshed separado.

Isso é evolução natural do que o manifesto atual já reconhecia: *"se o método ganhar componente executável, `plataforma` e `integração` deixam de ser inativos"*. É exatamente isso.

---

## O que fica pendente pra Fase E da refatoração

Este documento consolida a **tese**. A **spec** que virá a seguir (usando a `especificar` do método atual, em nível N3) precisa ainda resolver:

- **Ordem de execução da migração** — quais skills refatorar primeiro (Especificar? Homologar? Nova skill de Traduzir?); quais artefatos migrar em cada commit.
- **Nomes das skills novas** — Definir/Definidor, Desenhar/Designer, Traduzir/Validador, Implementar/Executor, Observar/Observador. Cada um vira uma skill ou o mesmo agente conduz múltiplas em subagentes distintos.
- **Hooks concretos** — quais primeiros hooks implementar (o repo atual não tem `.cursor/hooks.json` nem equivalente Claude Code; o mínimo viável precisa ser desenhado).
- **CI mínimo viável** — quais checks entram na primeira versão vs. quais ficam pra iteração seguinte.
- **Template de spec revisado** — o `template-especificacao.md` atual precisa acomodar a nova seção "contrato arquitetural" e o gate de falsificabilidade.
- **Documento de migração** — ECHO → SLE, com equivalências ("Fase C do ECHO ≈ Fases Desenhar+Traduzir+Implementar do SLE").
- **Skill `especificar` da própria refatoração** — teste de ácido do método atual: ele consegue especificar a própria substituição?

Nenhuma dessas pendências é ambiguidade da tese. São decisões operacionais que a Fase E vai resolver caso por caso.

---

*Este documento nasceu de uma sessão de design em 2026-08-07, conduzida sobre uso continuado das skills atuais e reconhecimento do parentesco com loop engineering (Osmani, jun/2026). Ele é o input para a próxima aplicação do método ECHO nele mesmo — a spec N3 dessa refatoração é o próximo passo, e vai testar se ECHO sobrevive a especificar a própria substituição.*

---

## Histórico de revisões

**v2 — 2026-08-07 (ajuste de fidelidade):** durante a Fase C da própria refatoração, foi identificada a *fissura da fidelidade* — protótipo descartado em N3 perde aspectos visuais/UX/microinteração que a consolidação não conseguiu nomear explicitamente, gerando frustração contratual entre o que foi homologado no protótipo e o que o Executor produziu do zero. Ajuste aplicado: protótipo passa a ser **preservado como artefato de fidelidade** (não descartado); Executor ganha acesso ao protótipo como referência (não como base de cópia); Validator ganha acesso ao protótipo apenas na Fase Traduzir para escrever testes de fidelidade (Camada 3, opcional) quando aplicável. Alterações refletidas em: matriz de visibilidade (linhas novas para *Protótipo N3 preservado* e *Testes de fidelidade*); seção *Regras do protótipo (só Nível 3)*; nova seção *Testes de fidelidade*; skills `designer`, `validator`, `executor` atualizadas em conjunto; spec e plano da refatoração atualizados para refletir o desvio.

**v1 — 2026-08-07:** tese original consolidada em sessão de design. Protótipo em N3 era descartado após consolidação, com a suposição de que aprendizado explícito seria integralmente capturado na spec enriquecida.
