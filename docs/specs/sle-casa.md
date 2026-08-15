# sle-casa

## Intenção
O `sle` ganha casa própria e um cadastro de repositórios que você edita à mão, para deixar de receber caminho a cada invocação.

## Depende de
`loop-cli` — os subcomandos e o código de saída.

## Critérios

**A casa**

- [ ] **H1** `[plataforma]` — A casa é `~/.sle/`, e a variável de ambiente `SLE_CASA` tem precedência sobre ela.
- [ ] **H2** `[plataforma]` — Casa ausente é criada na primeira execução que precise dela, e a criação é informada uma vez.
- [ ] **H3** `[plataforma]` — Nada da casa é escrito dentro de um alvo, e nada de alvo é escrito na casa. Rodar o `sle` não altera arquivo nenhum do projeto por causa de cadastro.

**O cadastro**

- [ ] **H4** `[integração]` — `<casa>/repos.md` declara os repositórios, um por linha, no formato `- <apelido>: <caminho>`. Linha fora do formato é recusada nomeando a linha.
- [ ] **H5** `[integração]` — `sle repo add <apelido> <caminho>` acrescenta ao arquivo **preservando o que já estava lá**: ordem, comentários e linhas em branco continuam como estavam.
- [ ] **H6** `[integração]` — Apelido já cadastrado é recusado, nomeando o caminho que ele já aponta. Nada é sobrescrito em silêncio.
- [ ] **H7** `[integração]` — `sle repo list` mostra apelido, caminho e se o caminho existe hoje.
- [ ] **H8** `[integração]` — `sle repo rm <apelido>` remove só aquela linha; apelido inexistente é recusado nomeando o que foi procurado.
- [ ] **H9** `[miolo]` — `--alvo` resolve primeiro como apelido cadastrado; não havendo apelido com aquele nome, trata o valor como caminho.
- [ ] **H10** `[plataforma]` — Caminho cadastrado que não existe mais não impede nenhum comando de funcionar: ele é reportado como ausente e os outros seguem.
- [ ] **H11** `[miolo]` — O cadastro é relido a cada invocação. Nada dele é guardado entre execuções além do próprio arquivo.

## Contrato técnico

- **Markdown editável, não JSON nem binário.** "Cadastro alterável" quer dizer que você abre e edita; formato que exige ferramenta para ser alterado quebra isso. O `sle repo add` é conveniência, não a única porta.
- **Sem banco de dados.** As três perguntas em jogo — quais repositórios existem, em que estado está um, como estão todos — são sobre o presente: a primeira é dado autorado e as outras duas se derivam dos artefatos do alvo. Um armazenamento que respondesse as duas últimas seria cache de estado derivado, e cache que diverge é como a ferramenta passa a mentir com confiança. O banco entra quando aparecer pergunta sobre o **passado**, com esquema desenhado para ela.
- `SLE_CASA` existe para separar ambientes e para a suíte não tocar a casa real de quem roda os testes.
- A casa guarda **dado autorado**; o estado de trabalho continua vivendo no alvo, em `.sle/loop.jsonl`, `docs/specs/` e nos vereditos.

## Fora de escopo

- **O painel.** É a próxima spec e depende desta: sem cadastro não há "todos os repositórios".
- **Histórico e banco.** Nenhuma pergunta atual precisa deles, e esquema desenhado sem pergunta vira adivinhação.
- **Ferramental de prototipagem.** A costura por onde ele entra é o insumo do pedido, e isso vem depois.
- **Sincronizar a casa entre máquinas.** Um arquivo versionável já resolve para quem quiser; sincronizar é produto, não ferramenta.
- **Configuração por repositório** (agente próprio, teto próprio). Só quando um repositório precisar diferir — hoje nenhum precisa.

## Plano

1. `tooling/loop/casa.py` — descoberta e criação da casa (H1, H2, H3).
2. `tooling/loop/repos.py` — leitura, escrita preservando o arquivo, e resolução de apelido (H4–H8, H10, H11).
3. `tooling/loop/driver.py` — o subcomando `repo` e a resolução de `--alvo` (H7, H8, H9).
4. `tooling/loop/tests/test_casa.py` e `test_repos.py`, com `SLE_CASA` apontando para diretório temporário.

Sem fatias: o cadastro não fecha sem a casa, e a casa sozinha não entrega nada.

## Perguntas em aberto

Nenhuma.
