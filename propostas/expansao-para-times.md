# Proposta (não validada): SLE para múltiplas pessoas/times

> **Status: hipótese, não mudança.** Isso não é uma extensão das skills — é o registro de um raciocínio, pra não perder o contexto e pra servir de ponto de partida quando (e se) houver evidência real de time justificando a mudança. Por enquanto, nenhuma linha das quatro skills (`designer`, `validator`, `executor`, `observer`) deve mudar por causa deste documento.

> **Nota histórica:** este documento foi escrito originalmente sobre o ECHO (v1 do método), quando havia três skills. Após a refatoração para SLE (v2), o raciocínio abaixo continua válido — mas ganha uma leitura nova: várias das mudanças que "precisariam acontecer antes disso virar mudança real" já foram absorvidas dentro do próprio método (enforcement determinístico via hooks e CI, gates humanos explícitos, Observer com skill própria). O texto abaixo preserva a forma original para documentar a evolução do raciocínio; ver footer para o mapeamento SLE → itens desta proposta.

## Por que isso está aqui, e não nas skills

O README já é explícito sobre isso: "difusão pro time só depois de eu conseguir defender cada parte com exemplo real, não com teoria." O raciocínio abaixo nasceu de uma conversa (não de um incidente real de time) — nenhum item aqui tem, ainda, uma história real por trás como as outras entradas de "o que ainda falta". Documentar aqui, fora das skills, é a forma de aplicar essa mesma regra a nós mesmos: registrar a ideia sem fingir que ela já foi validada.

## O raciocínio, resumido

A pergunta que originou isso: como o ciclo (ECHO na época, SLE hoje) se comporta quando sai de "uma pessoa + IA" pra "10+ pessoas"? A resposta, ainda hipotética: **o ciclo em si não muda de forma — o que falta é quem garante que ele foi seguido.** Solo, isso é disciplina pessoal. Em time, precisa virar estrutura que não depende de ninguém lembrar.

Isso se desdobra em seis eixos, todos ainda teóricos:

1. **De convenção pra gate.** Hoje seguir `especificar`/`planejar`/`homologar` depende de escolha. Em time, precisaria de enforcement real (PR sem spec linkada não abre revisão, cobertura de critério de aceite como check de CI) — o que já está mapeado como lacuna conhecida em "Enforcement ainda é probabilístico" no README, mas vale reforçar: isso é pré-requisito de qualquer expansão pra time, não um "nice to have" à parte.
2. **De arquivo solto pra sistema de registro.** `docs/specs/*.md` funciona pra contexto de uma pessoa; em time precisaria de ID rastreável (issue/ticket linkado), não só nome de arquivo.
3. **De nível autoavaliado pra critério codificado.** "Nível 1/2/3" por julgamento não escala com calibre de risco diferente por pessoa — precisaria de critério objetivo (raio de impacto, reversibilidade, dado sensível).
4. **De autorrevisão guiada pra segunda pessoa com autoridade nomeada.** O checklist arquitetural de `homologar` pede que o usuário responda, não a IA — em time, precisaria ser respondido por quem tem autoridade sobre aquele domínio, não por quem estiver na conversa.
5. **De memória pessoal pra observabilidade real.** Fase O hoje é prática manual — em escala precisaria de sinal automático (error tracking, alertas) e gatilho formal (incidente Sev1/2 vira postmortem vira input de `especificar`).
6. **Calibrar pra não virar gargalo.** Com várias pessoas gerando spec o tempo todo, a válvula de escape do Nível 1 importa mais, não menos — e o critério do que qualifica precisa ser combinado pelo time, não decidido individualmente a cada vez.

## O que precisaria acontecer antes disso virar mudança real

- Pelo menos um incidente real de time (não hipotético) que essas mudanças resolveriam — ex: alguém aprovou uma spec que não deveria, ou um plano avançou sem o revisor certo saber.
- Ou um piloto deliberado: rodar o método com outra pessoa em paralelo, de propósito, pra gerar essa evidência antes de esperar o incidente acontecer sozinho.
- Só depois disso, os campos concretos (aprovador nomeado, referência externa/ticket, responsáveis por passo no plano) voltam a ser avaliados — e provavelmente um de cada vez, não os seis juntos.

---

## Nota de reconciliação com o SLE (v2 do método)

A refatoração para SLE absorveu, dentro do próprio método (não como extensão para time), várias mudanças que este documento listava como pré-requisitos para a expansão. Mapeamento:

- **Item 1 — "de convenção pra gate"** → resolvido no SLE por `tooling/hooks/` (enforcement in-session) e `tooling/ci/` (enforcement de repositório). As invariantes 1 e 2 (Designer ≠ Executor, Executor ≠ Validator) são deterministicamente checadas. Não é mais "hipótese para time", é infraestrutura instalada.
- **Item 3 — "de nível autoavaliado pra critério codificado"** → o SLE mantém autoavaliação (N1/N2/N3), mas adiciona o falsifiability gate: cada critério da spec precisa ser objetivamente falseável, o que reduz a variância entre avaliadores. Ainda não é critério totalmente codificado — segue sendo um item para pilotar em time.
- **Item 5 — "de memória pessoal pra observabilidade real"** → o SLE tem skill `observer` com dois modos (event-driven / cadence-driven) e log estruturado `.sle/pressao-metodo.md`. Não substitui error tracking de time, mas dá um receptáculo formal para sinais.
- **Itens 2, 4, 6** — seguem válidos como propostas não-validadas para time (ID rastreável em ticket, aprovador nomeado por domínio, calibração de N1 combinada pelo time). São o que ainda pede piloto real antes de virar mudança.

*Este documento nasceu de uma sessão real de trabalho (2026-07-11), registrado como aprendizado a partir da própria disciplina que o método pede: nenhuma mudança de processo sem evidência, nem quando a mudança é no próprio processo.*
