# versao-limpa-das-skills

## Intenção
As skills do SLE passam a carregar e operar de forma previsível fora do Claude Code, com uma definição explícita de portabilidade aprovada no gate.

## Depende de
nenhuma.

## Critérios
- [ ] **C1** `integração` — "Limpa" significa **formato genérico único** para qualquer harness, preservando os princípios já vigentes do método.
- [ ] **C2** `integração` — As seis skills (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`, `prototipar-frontend`) têm frontmatter YAML válida no repositório.
- [ ] **C3** `integração` — As três skills que hoje falham no Cursor (`especificar`, `codificar`, `prototipar-frontend`) passam a carregar no mesmo mecanismo usado para as demais.
- [ ] **C4** `plataforma` — O campo `disable-model-invocation: false` deixa de existir nas seis skills, sem regressão de comportamento.
- [ ] **C5** `integração` — A forma canônica das definições em `.claude/agents/` segue o formato genérico único de C1, sem especializações por harness.
- [ ] **C6** `plataforma` — O repositório deixa de depender de cópia antiga instalada em `~/.claude/skills/` para funcionar no fluxo atual; a fonte versionada passa a ser suficiente.
- [ ] **C7** `plataforma` — A documentação operacional (`README.md` e/ou doc em `docs/`) registra como validar a carga das seis skills no(s) harness(es) coberto(s) pela decisão de C1.
- [ ] **C8** `integração` — `docs/specs/plugin-cursor.md` deixa de ficar bloqueada por parse de skill: o pré-requisito técnico de "as seis skills carregam" fica atendido por esta spec.

## Contrato técnico
- Frontmatter de skill deve ser compatível com parser YAML estrito (incluindo casos com `: ` dentro de texto).
- A decisão de C1 governa estrutura de arquivos e contrato de compatibilidade: nenhuma implementação híbrida implícita.
- "Manter todos os princípios atuais" significa que esta spec altera forma de portabilidade e compatibilidade entre harnesses, sem alterar fases, invariantes ou gates do método.
- Nada além do padrão do repositório.

## Fora de escopo
- Reescrever M14/M15 de `plugin-cursor` — isso é da própria spec `plugin-cursor`.
- Implementar a análise de impacto multi-repo e o ciclo com solicitante/aprovador separados — essas demandas seguem como specs próprias.
- Corrigir a regressão de `bash`/WSL dos testes de `scripts/install.sh` — pedido independente.

## Plano
1. Registrar no texto da spec a decisão aprovada no gate: formato genérico único para qualquer harness, com preservação explícita dos princípios atuais do método.
2. Ajustar frontmatter das skills em `especificar/SKILL.md`, `codificar/SKILL.md`, `verificar/SKILL.md`, `homologar/SKILL.md`, `orquestrar/SKILL.md` e `prototipar-frontend/SKILL.md` para formato válido e sem `disable-model-invocation: false`.
3. Aplicar a estrutura definida no passo 1 para as definições em `.claude/agents/sle-codificar.md`, `.claude/agents/sle-verificar.md` e `.claude/agents/sle-homologar.md`.
4. Atualizar documentação de uso/validação em `README.md` e, se necessário, em `docs/` para refletir o contrato escolhido e o procedimento de verificação de carga.
5. Executar validação de carga no fluxo do Cursor (e no Claude Code, se coberto pela escolha do gate) e registrar evidência no artefato de veredito desta spec.

## Perguntas em aberto
nenhuma.
