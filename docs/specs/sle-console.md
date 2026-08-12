# sle-console

## Intenção
Você entra no `sle` e trabalha de dentro: seleciona um repositório, vê o que ele espera, e dispara as fases sem repetir caminho a cada comando.

## Depende de
`sle-casa` (o cadastro que o console manipula) e `sle-painel` (o que ele mostra como tarefa).

## Critérios

**Entrar e sair**

- [ ] **N1** `[integração]` — `sle console` entra no modo interativo.
- [ ] **N2** `[integração]` — `sle` sem subcomando entra no console **quando a entrada e a saída são terminal**; sem terminal, mantém a ajuda e a saída 2 de hoje.
- [ ] **N3** `[integração]` — `sair` e o fim de entrada (Ctrl-D) encerram a sessão com código 0.

**Trabalhar de dentro**

- [ ] **N4** `[experiência]` — O prompt mostra o repositório selecionado, ou diz que não há nenhum.
- [ ] **N5** `[miolo]` — `usar <apelido>` seleciona um repositório do cadastro; apelido desconhecido é recusado nomeando o que foi procurado, e a sessão continua.
- [ ] **N6** `[miolo]` — Com repositório selecionado, `pedir`, `rodar` e `tarefas` não exigem `--alvo`.
- [ ] **N7** `[miolo]` — Sem repositório selecionado, esses comandos recusam dizendo que falta selecionar — nunca escolhem um por conta.
- [ ] **N8** `[integração]` — Os comandos do console têm os mesmos nomes dos subcomandos: `repo`, `painel`, `pedir`, `rodar`. `tarefas` é o painel do repositório selecionado.

**Não derrubar a sessão**

- [ ] **N9** `[experiência]` — Comando desconhecido informa e a sessão continua.
- [ ] **N10** `[plataforma]` — Erro dentro de um comando é informado e a sessão continua. Nada além de `sair` e do fim de entrada encerra o console.
- [ ] **N11** `[plataforma]` — `pedir` e `rodar` rodam de dentro do console e a sessão **espera** até terminarem; a sessão interativa do agente recebe o terminal enquanto isso.

**Não duplicar regra**

- [ ] **N12** `[miolo]` — O console chama as mesmas funções que os subcomandos. Substituir `driver.rodar` muda o comportamento do console também.
- [ ] **N13** `[miolo]` — A seleção de repositório vive só na sessão: sair e entrar de novo começa sem seleção, e nada é gravado por causa dela.

## Contrato técnico

- **Emenda declarada ao `S3` da `loop-cli`.** Ele dizia "sem subcomando, ajuda e saída não-zero", sem qualificar. Passa a valer só fora de terminal. O que o `S3` protegia — script que encadeia `sle` e lê o código de saída — continua protegido, porque script não tem terminal. `S6` e `S7` seguem intactos.
- Detecção por `isatty()` **nas duas pontas**, entrada e saída: só uma delas mente em ambiente de CI.
- `readline` quando disponível, para histórico e edição de linha. Ausência degrada, não bloqueia — e nenhuma dependência externa entra por causa disso.
- **O console é despacho, não lógica.** É o que o `N12` cobra, e é o que impede duas portas de entrada divergirem no comportamento — que é exatamente o defeito que uma interface nova costuma introduzir.
- A seleção fica em memória. Persistir "último repositório usado" seria estado autorado sem ninguém ter autorado, e reabriria a porta de a ferramenta agir sobre um alvo que você não escolheu nesta sessão.

## Fora de escopo

- **Completar comando com Tab.** Depende de `readline` estar presente e de as opções virarem dado; é conforto, e conforto entra depois do que funciona.
- **Rodar fase em segundo plano.** `rodar` bloqueando é o comportamento honesto: o loop já escreve no repositório, e soltá-lo em paralelo com você digitando no mesmo alvo é como se cria conflito de working tree.
- **Vários repositórios selecionados ao mesmo tempo.** Uma fase por vez continua sendo regra; seleção múltipla sugeriria o contrário.
- **Configuração de aparência, cor ou tema.** Não muda o que a ferramenta responde.

## Plano

1. `tooling/loop/console.py` — o laço de leitura, o despacho para as funções existentes e a sessão (N1, N3–N13).
2. `tooling/loop/driver.py` — o subcomando `console` e a regra do terminal em `main` (N1, N2).
3. `tooling/loop/tests/test_console.py`, com entrada e saída simuladas e as funções de fase substituídas.

Sem fatias: o laço não fecha sem o despacho, e o despacho sozinho não é console.

## Perguntas em aberto

Nenhuma.
