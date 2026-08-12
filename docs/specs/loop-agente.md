# loop-agente

## Intenção
O loop deixa de fixar o Claude Code: qualquer agente com modo headless que resolva as skills roda as fases, e o loop recusa começar se a skill instalada divergir da do clone.

## Depende de
`roteador-driver` — é ele que monta o prompt e chama o processo.

## Critérios

**O comando é configuração**

- [ ] **G1** `[integração]` — O comando de invocação é configurável por parâmetro. Nenhum executável fica fixo no código do laço.
- [ ] **G2** `[integração]` — Sem configuração, o comando é `claude -p <prompt>`.
- [ ] **G3** `[integração]` — O template aceita o prompt em posição declarada, não presumida no fim: um agente que exija o texto antes de outras flags é configurável sem mudar código.
- [ ] **G4** `[integração]` — Template sem o marcador de prompt é recusado **antes** da primeira invocação, nomeando o marcador que falta.
- [ ] **G5** `[plataforma]` — Comando cujo executável não existe no PATH resulta em `escalar` nomeando o executável procurado. Nunca em stack trace.

**Você fica sabendo qual skill vai rodar**

- [ ] **G6** `[plataforma]` — Antes de começar, o driver compara cada uma das quatro skills instaladas com a do clone e **avisa** nomeando as que divergem. A execução continua.
- [ ] **G7** `[plataforma]` — Skill ausente na instalação é avisada como ausência, não como diferença de conteúdo.
- [ ] **G8** `[plataforma]` — Instalação em escopo local (`<alvo>/.claude/skills/`) tem precedência sobre a global na comparação, porque é ela que o agente vai usar.

**O prompt**

- [ ] **G9** `[integração]` — O prompt cita a skill pelo nome e passa os insumos que ela declara: caminho da spec e alvo para `codificar`; mais o ref base para `verificar`.
- [ ] **G10** `[integração]` — O prompt não contém o corpo da spec nem o do veredito, só caminhos. Quem lê os arquivos é a fase, dentro da sessão dela.

**A decisão não muda**

- [ ] **G11** `[miolo]` — O mesmo lote, rodado com dois comandos diferentes, produz a mesma sequência de decisões. Trocar de agente não muda uma linha do roteamento.

## Contrato técnico

- Template do comando como lista de argumentos com o marcador `{prompt}` num deles — ex.: `claude -p {prompt}`, `agent -p {prompt}`.
- **Skills continuam sendo citadas por nome, não embutidas no prompt.** O agente do Cursor importa as skills do Claude e aceita `-p`, então os dois alvos resolvem skill nativamente; embutir o markdown reimplementaria no prompt o que o harness já faz, a cada invocação. A guarda do `G6` cobre o risco que embutir cobriria.
- **Avisa, não trava.** Divergência é informação, não impedimento: travar obrigaria a reinstalar a cada linha editada numa skill, e o loop passaria a atrapalhar justamente quem está desenvolvendo o método. As guardas que travam (`branch default`, `working tree sujo`) protegem o repositório de quem roda; esta protege quem lê o resultado, e um aviso basta.
- **Compara conteúdo, não data.** Hash do texto: data de arquivo mente depois de um `git checkout`.
- Escopo procurado: `<alvo>/.claude/skills/<nome>/SKILL.md` primeiro, `~/.claude/skills/<nome>/SKILL.md` depois. As quatro skills são `especificar`, `codificar`, `verificar`, `homologar`.
- Nada disto toca `roteador.py`, `lote.py`, `veredito.py`, `secoes.py` ou `dependencia.py`, e o teste de pureza continua valendo.

## Fora de escopo

- **Embutir o SKILL.md no prompt.** Só faz sentido para um agente que não importe skills, e nenhum dos dois alvos é assim. Se aparecer, é uma demanda de um critério, não um modo a manter agora.
- **Reinstalar sozinho quando a guarda falhar.** O loop avisa e para; rodar o instalador é decisão sua, e escrever em `~/.claude/` sem você pedir é o tipo de mágica que ninguém quer descobrir depois.
- **Adaptar o formato de saída de cada agente** — o driver não interpreta saída, só exit code e artefato. É o que torna essa portabilidade barata.
- **Descobrir agente instalado automaticamente** — adivinhar qual usar falha em silêncio na máquina de outra pessoa.
- **Paridade de comportamento entre agentes** — dois podem produzir código diferente para a mesma spec. Quem mede é `verificar`.

## Plano

1. `tooling/loop/invocacao.py` — template configurável, validação do marcador e do executável (G1–G5).
2. `tooling/loop/skills_instaladas.py` — localização por escopo, comparação por hash e a mensagem de divergência (G6–G8).
3. `tooling/loop/driver.py` — a guarda na abertura, junto das que já existem, e o prompt (G9, G10).
4. `tooling/loop/tests/test_invocacao.py`, `test_skills_instaladas.py` e `test_driver.py`, com o teste de dois comandos e a mesma sequência (G11).

## Perguntas em aberto

Nenhuma.
