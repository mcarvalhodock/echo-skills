# Spec: Decomposição por domínio na Fase E do ECHO

> Nível 3 — mudança arquitetural no método ECHO. Vive em branch experimental, não em `main`.

## Intenção
A skill `especificar` passa a produzir specs de Nível 2 e 3 com uma seção "Domínios envolvidos" que mapeia cada critério de aceite e caso de borda a um ou mais domínios de um catálogo fechado, permitindo que subagentes especialistas peguem apenas a fatia que lhes corresponde sem reinterpretar o conjunto.

## Contexto
Hoje a spec ECHO é entregue como bloco único. Quando a tarefa cruza domínios (ex: segurança + coding), o mesmo executor precisa alternar de perspectiva — diluindo a precisão que subagentes especializados poderiam trazer. A hipótese: se a spec já vier marcada por domínio, cada slice pode ser delegada a um especialista sem retrabalho de interpretação.

## Critérios de aceite
- [ ] Template de spec Nível 2 (`template-especificacao.md`) tem uma seção nova chamada "Domínios envolvidos" documentada.
- [ ] Template de spec Nível 3 tem a mesma seção "Domínios envolvidos" com estrutura idêntica à do N2.
- [ ] Template Nível 1 (Micro) permanece inalterado.
- [ ] Um catálogo fechado com exatamente 6 domínios — `segurança`, `coding`, `testes`, `infra`, `ux`, `performance` — está documentado em local único (dentro do próprio `template-especificacao.md`) e é a fonte de verdade para a skill.
- [ ] A skill `especificar` (`especificar/SKILL.md`) conduz o preenchimento da seção "Domínios envolvidos" ao gerar specs N2/N3, incluindo verificação de que cada critério de aceite e cada caso de borda listado aparece marcado em pelo menos um domínio.
- [ ] A skill `especificar` recusa domínio fora do catálogo (não aceita "outros", "diversos" ou nomes inventados) e oferece o catálogo canônico quando o usuário tenta usar um nome fora dele.
- [ ] Um critério de aceite pode aparecer em múltiplos domínios simultaneamente (cross-cutting é permitido e explícito).
- [ ] A "regra de fechamento: zero perguntas penduradas" da skill continua se aplicando à nova seção — nenhuma spec pode ser apresentada como pronta com critério/caso de borda sem domínio atribuído.
- [ ] As skills `planejar/SKILL.md` e `homologar/SKILL.md` **não** são alteradas nesta mudança.
- [ ] Toda a mudança vive em branch `experimento/decomposicao-por-dominio` a partir de `main`; `main` não é tocada até decisão explícita de promover.

## Casos de borda considerados
- Critério de aceite genuinamente cross-cutting (ex: "token expira em ≤ 15min" toca segurança e performance) — permitido, marcar em ambos os domínios.
- Tarefa mono-domínio (ex: refactor puro em `coding`) — a seção existe e lista apenas 1 domínio, sem inflar artificialmente.
- Usuário sugere domínio fora do catálogo — skill recusa, oferece a lista canônica, e a sugestão fica anotada informalmente como candidata a revisão futura do catálogo (não vai pra dentro da spec).
- Domínio marcado na seção sem nenhum critério apontando pra ele — sinal de decomposição vaga; skill pede refino antes de fechar.
- Caso de borda cross-cutting — mesma regra que critério: pode aparecer em múltiplos domínios.

## Fora de escopo
- Alteração em `planejar/SKILL.md` ou `homologar/SKILL.md` (fica para spec futura).
- Orquestração real de subagentes: dispatch, coordenação, merge de outputs — problema da Fase C, não da Fase E.
- "Aprovador nomeado por domínio" (quem responde pelo domínio X) — é o assunto de `propostas/expansao-para-times.md`, não confundir com esta mudança.
- Nomear subagente específico dentro da spec (ex: `@security-agent`) — spec só nomeia o **domínio**, não o executor.
- Migração forçada de specs antigas — compatibilidade retroativa, specs existentes continuam válidas sem a seção nova.

## Restrições
- Compatibilidade retroativa: specs escritas no formato anterior continuam legíveis; a nova seção é aditiva.
- Sem dependências novas: mudança é 100% em markdown.
- Fonte única de verdade para o catálogo (`template-especificacao.md`) — a skill referencia, não duplica.
- Preservar a legibilidade atual do template: seção separada, sem poluir critérios com tags inline.
- A regra de fechamento continua sendo o princípio norteador.

## Ambiente / destino
- Repositório: `C:\dock-codes\echo-skills`.
- Branch de trabalho: `experimento/decomposicao-por-dominio` (criada a partir de `main`).
- Arquivos previstos para alteração: `especificar/SKILL.md`, `template-especificacao.md`. `metodologia-echo.md` pode receber uma referência curta à seção nova, mas não muda estrutura.
- Spec salva em: `docs/specs/decomposicao-por-dominio.md`.
- Skills instaladas globalmente em `~/.claude/skills/` **não** são tocadas: só o repo, para permitir testes locais isolados.

## Nível de risco
- [x] Difícil de reverter em tese (mexe na arquitetura do método), **mas mitigado** por viver em branch experimental — reversão real é `git branch -D`. Escala mantida como Nível 3 porque a decisão de design é arquitetural, ainda que o custo técnico de reverter seja baixo.

## Alternativas consideradas
1. **Decomposição vive no plano (Fase C/`planejar`)** — descartada: colocar na spec deixa a fatia disponível já na fase mais precoce, e evita que o subagente tenha que ler o plano inteiro pra achar o que é dele.
2. **Fase nova entre E e C (skill "Decompor")** — descartada por simplicidade: introduziria uma quarta transição, e o valor cabe dentro da própria Fase E.
3. **Catálogo aberto (IA nomeia domínios livremente por tarefa)** — descartada: comprometeria consistência entre specs e a especialização de subagentes; cada spec inventaria nomes diferentes pra coisas parecidas.
4. **Tag inline em cada critério (ex: `- [seguranca] critério X`)** — descartada por poluir leitura; a seção separada preserva a clareza atual do template.

## Dependências e impacto
- `especificar/SKILL.md`: Passo 2 (preenchimento) precisa incluir a nova seção; Passo 3 (fechamento) estende a validação para cobrir o novo campo.
- `template-especificacao.md`: adiciona o catálogo fechado + a seção "Domínios envolvidos" nos blocos N2 e N3, sem tocar no N1.
- `metodologia-echo.md`: nota curta em "Fase 1 — Especificar" mencionando a decomposição por domínio (opcional; se preferir, fica sem).
- `planejar` e `homologar`: sem alteração aqui. Ficam com input mais rico e podem evoluir depois pra usar a decomposição — próxima spec.
- Uso manual do template fora da skill: nada quebra; usuários manuais podem preencher ou deixar em branco sem consequência.

## Plano de verificação
- Rodar a skill `especificar` modificada localmente contra pelo menos 3 tarefas reais: 2 em Nível 2 e 1 em Nível 3.
- Observar em cada rodada:
  - Cada critério e caso de borda ganha domínio sem ficar pendurado (regra de fechamento respeitada).
  - Cross-cutting aparece naturalmente quando faz sentido, sem ser forçado.
  - Catálogo fechado se sustenta ou surge necessidade real de um 7º domínio.
- Teste negativo: pedir explicitamente à skill um domínio fora do catálogo (ex: "compliance") e verificar que ela recusa e oferece a lista.
- Teste de regressão: gerar uma spec Nível 1 e verificar que ela sai idêntica ao formato atual (sem seção nova).
- Nenhuma suíte automatizada — método vive em markdown; verificação é executiva e humana.

## Decisão de reversibilidade
- Tudo em branch `experimento/decomposicao-por-dominio`. `main` intocada.
- Reversão local: `git checkout main && git branch -D experimento/decomposicao-por-dominio`.
- Reversão remota (se subida): `git push origin --delete experimento/decomposicao-por-dominio`.
- Skills instaladas em `~/.claude/skills/` continuam apontando para as versões atuais (sem seção de domínios) até decisão manual de promover — nenhum efeito colateral sobre o fluxo em uso.

## Perguntas em aberto
- **Emergência de 7º domínio**: se os testes reais mostrarem que o catálogo fechado é insuficiente, qual será o critério pra promover um novo domínio ao catálogo canônico (versus tratar o caso como pontual e permanecer com 6)? Isso é decisão de governança do método, provavelmente vira input da Fase O desta própria mudança — nomeada aqui como incerteza consciente, não como decisão técnica esquecida.
- **Interação futura com `planejar`**: quando `planejar` for atualizado (próxima spec, fora deste escopo), o desenho atual da seção "Domínios envolvidos" será utilizável como está, ou vai precisar ser refeito? Só saberemos com uso real.

---

*Spec gerada pela skill `especificar` (Fase E do método ECHO) em 2026-07-28. Próximo passo: skill `planejar`.*
