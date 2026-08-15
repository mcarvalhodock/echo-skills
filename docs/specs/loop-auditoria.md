# loop-auditoria

## Intenção
Antes de fechar o ciclo, todos os critérios do alvo são relidos contra o código que existe agora — não contra o que existia quando cada spec foi construída.

## Depende de
`loop-cli` — é ele que fecha o lote e invoca `homologar`.

## Critérios

**Quando e sobre o quê**

- [ ] **F1** `[miolo]` — Fechado o lote, a auditoria roda **antes** de `homologar`.
- [ ] **F2** `[miolo]` — A auditoria cobre **todas** as specs de `<alvo>/docs/specs/`, não apenas as do ciclo corrente.
- [ ] **F3** `[miolo]` — Spec em quarentena não é auditada: ela não foi construída, e cobrar critério dela seria reprovar trabalho que ninguém fez.
- [ ] **F4** `[plataforma]` — Cada invocação da auditoria conta no fusível, como qualquer outra.

**Como se lê**

- [ ] **F5** `[integração]` — Cada spec é auditada por uma leitura limpa **própria**, uma invocação por spec.
- [ ] **F6** `[integração]` — O molde pede leitura contra o **estado atual** do escopo, sem ref base e sem diff.
- [ ] **F7** `[miolo]` — Nenhum arquivo de skill muda, e o molde da leitura limpa tem **um só dono em código**. Um teste amarra o texto que a auditoria emite ao molde escrito em `verificar/SKILL.md`: divergir entre os dois reprova.

**O que fica escrito**

- [ ] **F8** `[integração]` — O resultado de cada spec vai para `<alvo>/docs/specs/<nome>-auditoria.md`.
- [ ] **F9** `[integração]` — O veredito da demanda (`<nome>-veredito.md`) não é sobrescrito, movido nem apagado. As duas perguntas são diferentes: *foi atendido quando foi construído* e *continua sendo verdade*.

**O que acontece depois**

- [ ] **F10** `[miolo]` — Qualquer critério `não atendido` ou `não verificável` em qualquer auditoria resulta em `escalar` com motivo `regressao-de-criterio`, e `homologar` **não** roda.
- [ ] **F11** `[miolo]` — Auditoria inteiramente `atendido` segue para `homologar`, como hoje.
- [ ] **F12** `[miolo]` — Ao escalar, o relato nomeia as specs que regrediram e o caminho das auditorias — e **não** transcreve o conteúdo delas.

## Contrato técnico

- **Isto custa uma invocação por spec.** Neste repositório são treze, e cresce com o alvo. É o preço de não confiar em veredito velho, e está declarado aqui para não ser descoberto na conta.
- O molde é o mesmo da leitura limpa, na variante sem diff que já existe para alvo sem git: *"leia a spec e o estado atual de `<escopo>`"*.
- **Não existe emissor do molde em código hoje** — ele vive em prosa dentro de `verificar/SKILL.md`, e a fase o emite de dentro da própria sessão. A auditoria é o primeiro lugar que precisa dele em código, e daí nasce o risco de duas cópias divergirem, que é o mesmo que já mordeu com skill instalada versus skill do clone. Por isso o molde ganha um dono único em código e um teste que o amarra ao texto da skill. **Reusar `driver.prompt_de(VERIFICAR)` seria pior**: aquele emissor cita uma skill que não está em jogo e afirma "sem git no alvo", que aqui é falso.
- **Auditoria antes de `homologar`, e não depois**, porque checklist de arquitetura sobre código com critério regredido é pergunta prematura: primeiro se descobre que está quebrado, depois se pergunta se o desenho aguenta o triplo do volume.
- `regressao-de-criterio` é motivo próprio e não se confunde com `defeito-de-spec`: lá o critério não era mensurável; aqui ele era, foi atendido, e deixou de ser.
- A auditoria **não** volta para `codificar` automaticamente. Critério que regrediu depois de fechado pode ter três causas — código quebrou, critério envelheceu, ou o veredito original errou — e escolher entre elas é julgamento seu.

## Fora de escopo

- **Auditar a cada demanda.** Seria pagar N leituras por spec fechada; é no fim do ciclo que a pergunta "ainda é verdade?" tem sentido.
- **Consertar sozinho o que regrediu.** As três causas possíveis levam a saídas diferentes, e só uma delas é "volta para codificar".
- **Auditar specs de outro alvo.** Cada alvo responde pelos seus critérios.
- **Substituir a suíte.** A auditoria lê critério; a suíte executa código. Uma pega promessa quebrada, a outra pega comportamento quebrado, e nenhuma cobre a outra.
- **Guardar histórico das auditorias.** O arquivo é sobrescrito a cada ciclo; acumular é pergunta sobre o passado, e nenhuma foi feita ainda.

## Plano

1. `tooling/loop/auditoria.py` — a lista de specs auditáveis, o prompt por spec e a leitura do resultado (F2, F3, F5, F6, F8).
2. `tooling/loop/driver.py` — a auditoria entre o fim do lote e `homologar`, o motivo novo e o relato (F1, F4, F7, F9–F12).
3. `tooling/loop/tests/test_auditoria.py`, com executor falso escrevendo auditorias verdes e vermelhas.

Sem fatias: a decisão de seguir ou escalar não fecha sem a leitura, e a leitura sozinha não muda nada.

## Perguntas em aberto

Nenhuma.
