# sle-ferramenta

## Intenção
Dentro do console você escolhe qual CLI de agente usar — ao abrir a sessão, no meio dela, ou só naquela chamada.

## Depende de
`sle-console` (a sessão) e `loop-agente` (o comando configurável).

## Critérios

**Ao abrir**

- [ ] **W1** `[integração]` — `sle console --comando <t>` e `--comando-interativo <t>` definem os comandos daquela sessão.
- [ ] **W2** `[integração]` — Sem esses argumentos, a sessão abre com o default de hoje: `claude -p {prompt}` no headless e `claude {prompt}` no interativo.

**No meio da sessão**

- [ ] **W3** `[experiência]` — `ferramenta`, sem argumento, mostra os dois comandos em vigor.
- [ ] **W4** `[miolo]` — `ferramenta --comando <t>` e `ferramenta --interativo <t>` trocam o comando para o resto da sessão, e a troca vale nas invocações seguintes.
- [ ] **W5** `[miolo]` — Template sem o marcador `{prompt}` é recusado nomeando o marcador que falta, e a sessão **segue com o anterior** — nunca fica sem comando.
- [ ] **W9** `[experiência]` — `ferramenta <nome>` troca pelos dois comandos daquele agente de uma vez, com a mesma economia de `usar <apelido>`. Os nomes são `claude` e `cursor`.
- [ ] **W10** `[experiência]` — Nome desconhecido é recusado **listando os que existem**, e a sessão segue com o anterior.

**Precedência**

- [ ] **W6** `[miolo]` — Comando passado na própria linha (`rodar … --comando <t>`) vale só naquela chamada e sobrepõe o da sessão.
- [ ] **W7** `[miolo]` — Terminada aquela chamada, a sessão volta ao comando dela.

**Nada é gravado**

- [ ] **W8** `[plataforma]` — Sair e entrar de novo volta ao default. Nenhum arquivo é criado ou alterado por causa da troca, nem na casa nem no alvo.

## Contrato técnico

- **Precedência: chamada > sessão > default.** O console anexa os argumentos da sessão **antes** do resto da linha, e o `argparse` fica com a última ocorrência — que é a que você digitou.
- **O default não muda, e o `G2` da `loop-agente` continua valendo sem emenda.** Trocar o default global mexeria num critério fechado e mudaria o comportamento de quem só usa a linha de comando.
- **Dois nomes conhecidos, e o template continua existindo.** `claude` expande para `claude -p {prompt}` e `claude {prompt}`; `cursor` expande para `agent -p {prompt}` e `agent {prompt}`. O nome existe pela simetria com `usar`: num console, colar template a cada troca é fricção que faz a pessoa não trocar. O template segue disponível para o que o nome não cobre — outro agente, ou o **caminho completo**, que importa porque `agent` é genérico o bastante para colidir com outro executável no PATH.
- **O executável do Cursor é `agent`**, informado por quem usa. Não está instalado na máquina onde isto foi escrito, então a expansão do nome `cursor` nunca foi exercitada de verdade — só a recusa da guarda por executável ausente.
- A troca **não** confere se o executável existe: quem faz isso é a guarda, na hora de invocar, e ela já nomeia o que faltou. Conferir duas vezes daria duas mensagens para o mesmo problema.
- O estado da ferramenta vive na sessão, como a seleção de repositório: persistir seria dado autorado que ninguém autorou.

## Fora de escopo

- **Nome novo sem agente novo.** A lista tem dois porque existem dois; um terceiro entra quando alguém usar um terceiro, não por simetria de catálogo.
- **Gravar a escolha na casa ou por repositório.** As duas são possíveis pela regra do dado autorado, e nenhuma foi pedida.
- **Mudar o default do `sle` fora do console.** É o `G2`, e ele está fechado.
- **Validar o executável na troca.** É da guarda, e duplicar a checagem duplicaria a mensagem.

## Plano

1. `tooling/loop/driver.py` — os dois argumentos no subparser `console` (W1, W2).
2. `tooling/loop/console.py` — o estado da sessão, o comando `ferramenta` com nome e com template, e a ordem de precedência no despacho (W3–W10).
3. `tooling/loop/tests/test_console.py` — os casos novos, com as funções de fase substituídas.

Sem fatias: o comando `ferramenta` não fecha sem o estado da sessão, e o estado sozinho não é observável.

## Perguntas em aberto

Nenhuma.
