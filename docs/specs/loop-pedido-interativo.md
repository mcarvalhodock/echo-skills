# loop-pedido-interativo

## Intenção
`especificar` volta a ser uma conversa: a fila abre uma sessão interativa por pedido, onde o agente pergunta e aprofunda, em vez de escrever a spec a partir de um parágrafo.

## Depende de
`loop-especificar` — é a fila que passa a abrir sessão em vez de invocar headless.

## Critérios

**A sessão é conversa**

- [ ] **Q1** `[integração]` — `especificar` roda em sessão interativa: o processo herda o terminal, e a saída dele **não** é capturada nem lida pelo driver.
- [ ] **Q2** `[integração]` — O comando interativo é configurável e, por default, **não** carrega a flag de modo headless que o segmento 2 usa.
- [ ] **Q3** `[plataforma]` — A fila espera cada sessão terminar antes de abrir a próxima. Nunca duas ao mesmo tempo.
- [ ] **Q4** `[plataforma]` — Terminada a sessão, a existência de `<alvo>/docs/specs/<nome>.md` continua sendo cobrada; ausência resulta em `escalar`, como hoje.
- [ ] **Q5** `[miolo]` — O segmento 2 continua headless. Nenhuma invocação de `codificar`, `verificar` ou `homologar` passa a herdar o terminal.

**O insumo não trava o loop**

- [ ] **Q6** `[plataforma]` — `pedidos.md` não conta como sujeira na guarda de working tree. Hoje o loop se bloqueia por causa do próprio insumo.
- [ ] **Q7** `[plataforma]` — Antes de abrir a fila, `pedidos.md` não versionado ou modificado vira um commit próprio, com assunto `loop(pedidos): registrar pedidos` e trailer `SLE-Loop: pedidos#registro`.
- [ ] **Q8** `[plataforma]` — `pedidos.md` já versionado e sem modificação não gera commit.

**O ensaio continua existindo**

- [ ] **Q9** `[plataforma]` — Em modo seco a fila é listada e **nenhuma sessão é aberta**, nem commit é feito.

## Contrato técnico

- **Interativo é ausência de captura.** O processo é lançado sem redirecionar `stdin`/`stdout`/`stderr`, para que a conversa aconteça no seu terminal. Não é uma flag do agente: é o driver não se meter entre você e ele.
- **Isso reforça a regra do `D3`, não a fere.** A decisão nunca usou o texto de retorno de uma fase; agora não existe texto de retorno para usar. `Resultado.saida` fica vazio nesse modo, e isso é honesto — ninguém leu.
- Comando interativo default: `claude {prompt}`, sem `-p`. O `{prompt}` semeia a primeira mensagem da conversa; o resto é você e o agente.
- A exceção de `pedidos.md` na guarda vale **só para esse caminho**, com o mesmo cuidado da escrituração do loop: prefixo solto engoliria `pedidos-antigos.md`, que é arquivo de alguém.
- O commit dos pedidos vem **antes** da primeira sessão, não junto da primeira spec: assim o log diz o que foi pedido separado do que foi especificado, e um `git show` do commit de pedidos responde "o que eu tinha pedido mesmo?".

## Fora de escopo

- **Tornar `codificar` ou `verificar` interativos.** Lá a conversa não acrescenta: `codificar` tem a spec como contrato, e `verificar` mede contra ela. É em `especificar` que falta contexto, e só lá.
- **Capturar ou arquivar a transcrição da conversa.** Seria documentação sobre o trabalho, e a spec resultante já é o artefato.
- **Rodar a fila sem humano presente.** É o oposto do que esta demanda existe para consertar; se ninguém estiver no terminal, a sessão fica esperando.
- **Emendar o `P5` da `loop-especificar` para "não headless".** O critério dela descreve o conteúdo do prompt e continua valendo; o que muda é o modo de execução, e é isto aqui.

## Plano

1. `tooling/loop/invocacao.py` — `executar_interativo` sem captura e o template próprio (Q1, Q2).
2. `tooling/loop/git_alvo.py` — exceção de `pedidos.md` na guarda e `commitar_pedidos` (Q6, Q7, Q8).
3. `tooling/loop/driver.py` — a fila usa o modo interativo, e o commit dos pedidos precede a primeira sessão (Q3, Q4, Q5, Q9).
4. `tooling/loop/tests/test_interativo.py`, mais os testes de guarda em `test_git_alvo.py`.

## Perguntas em aberto

Nenhuma.
