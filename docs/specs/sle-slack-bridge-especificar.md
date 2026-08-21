# sle-slack-bridge-especificar

## Intenção
Um app do Slack + bridge sobre o Cursor SDK executa a fase `especificar` do método SLE em contexto isolado, com multi-turno na thread do Slack, e entrega a spec como PR num repo alvo — provando que o método roda no meio Slack sem depender de admin do Cursor.

## Depende de
nenhuma.

## Critérios
- [ ] **B1** `integração` — Existe um Slack app cujo owner é você, com escopos `app_mentions:read`, `chat:write` e `channels:history`, e um endpoint HTTP de Events API apontando para o bridge. Nome do app, endpoint e escopos documentados no `README.md` do repo do bridge.
- [ ] **B2** `integração` — Uma menção ao app em canal onde ele foi convidado dispara a criação de um Cursor cloud agent (via `Agent.create`), associado ao `thread_ts` do post original.
- [ ] **B3** `integração` — O `Agent.create` de B2 usa `cloud=CloudAgentOptions(repos=[<repo alvo>])`, `model` lido do env `CURSOR_MODEL` (default `composer-2.5`), `api_key` do env `CURSOR_API_KEY`, e o primeiro `agent.send` envia o texto do post do Slack como o pedido.
- [ ] **B4** `integração` — Toda mensagem `assistant` do `run` que contém texto vira reply na thread do Slack (`thread_ts` do evento original), preservando o texto na íntegra.
- [ ] **B5** `integração` — Uma mensagem na mesma thread do Slack, do mesmo user do post original, sem menção ao app, dispara `Agent.resume(agent_id)` seguido de `agent.send(texto_da_mensagem)`.
- [ ] **B6** `plataforma` — Uma tabela DynamoDB (`SleBridgeThreads`, chave primária `thread_ts`) mapeia `thread_ts → agent_id`, sobrevive a reinício do bridge, e é o único caminho de resolução de agent em B5.
- [ ] **B7** `integração` — Quando `run.wait()` retorna `status="finished"`, o Cloud Agent cria PR automático no repo alvo (via `auto_create_pr=True`).
- [ ] **B8** `integração` — Ao detectar o PR criado em B7, o bridge posta o URL do PR na thread do Slack correspondente.
- [ ] **B9** `segurança` — Toda requisição ao endpoint do bridge é validada com HMAC via `SLACK_SIGNING_SECRET` antes de qualquer chamada ao SDK; requisição inválida retorna 401 sem side effects.
- [ ] **B10** `segurança` — `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` e `CURSOR_API_KEY` vivem em AWS Secrets Manager e chegam à Lambda como variáveis de ambiente resolvidas na inicialização; nenhum deles aparece em arquivo commitado e o `.gitignore` do repo cobre `.env*` e artefatos de credencial.
- [ ] **B11** `integração` — `CursorAgentError` e `result.status="error"` são reportados no Slack com mensagens distintas: a primeira nomeia falha de setup (auth/config); a segunda cita `run.id` do agent para investigação.
- [ ] **B12** `plataforma` — O bridge tem testes unitários cobrindo (a) validação HMAC de B9, (b) decisão spawn-vs-resume de B2/B5, (c) formatação de texto assistant → Slack de B4, (d) tratamento dos dois erros de B11.
- [ ] **B13** `plataforma` — O `README.md` do repo do bridge documenta setup do Slack app, variáveis de ambiente, comando de deploy, e o fluxo end-to-end esperado.
- [ ] **B14** `integração` — Um exemplo real registrado em `docs/exemplo-end-to-end.md` do repo do bridge: post inicial no Slack → pelo menos 2 perguntas do agent → pelo menos 2 respostas humanas → PR criado no repo teste → URL postado na thread. Marcador `spec:B14`.

## Contrato técnico
- **Repo do bridge:** novo repo dedicado `sle-slack-bridge` sob `github.com/mcarvalhodock`.
- **Linguagem:** Python 3.12+, dependência principal `cursor-sdk`.
- **Runtime do agent:** **cloud**, sem fallback local nesta fatia. Enterprise plan do humano dá quota.
- **Cloud runtime carrega automaticamente plugins/settings do time.** As skills do SLE precisam estar em `.cursor/skills/` OU `.claude/skills/` do repo alvo — pré-requisito operacional, não trabalho deste bridge.
- **Gate humano** da spec produzida = review do PR gerado pelo cloud agent. Merge = aprovação. Nesta fatia, solicitante = aprovador (mesma pessoa).
- **Deploy:** AWS Lambda + API Gateway HTTP API. IaC via **AWS SAM** (escolha derivada de Lambda + Python + DynamoDB nativos; outro IaC funcional serve, desde que provisione API Gateway + Lambda + tabela DynamoDB + integração com Secrets Manager).
- **Secrets** em AWS Secrets Manager, lidos na inicialização da Lambda e injetados como env vars — a Lambda IAM role concede acesso somente aos três segredos nomeados.
- **Padrão de código:** definido no `.sle/manifesto.md` criado no passo 1 do plano.

## Fora de escopo
- Roteamento solicitante ≠ aprovador — assumido igual nesta fatia; spec própria depois.
- Fases `codificar`, `verificar`, `homologar` disparadas pelo Slack — spec própria.
- Multi-repo no cloud run (mais de um repo por agent) — spec própria.
- GitHub como meio alternativo — spec própria se/quando fizer sentido.
- Publicar plugin no Cursor Team Marketplace — bloqueado por admin do Cursor.
- Cadastrar as skills do SLE em `.cursor/skills/` ou `.claude/skills/` dos repos alvo — pré-requisito operacional, spec própria de distribuição.
- Retry automático, rate limiting, monitoring, alerting — spec de hardening se o MVP se pagar.
- Aprovação da instalação do app no Slack workspace — passo humano do admin do workspace, uma vez.

## Plano
1. Criar repo `sle-slack-bridge` com estrutura mínima: `README.md`, `.gitignore`, `.sle/manifesto.md`, `pyproject.toml` (dependência `cursor-sdk`, `boto3`, `pytest`), `src/`, `tests/`, `template.yaml` (SAM).
2. Implementar validação HMAC (B9) em `src/slack_auth.py` — testável isoladamente antes de qualquer integração externa.
3. Implementar store DynamoDB (B6) em `src/store.py` com interface `save(thread_ts, agent_id)` / `load(thread_ts)`, usando `boto3` em modo mockável para os testes.
4. Implementar handler de eventos do Slack (B2, B5) em `src/handler.py`, chamando o cliente SDK (`src/sdk_client.py`) para B3 e B4.
5. Implementar detecção de conclusão do run e postagem do PR link (B7, B8) em `src/completion.py`.
6. Implementar tratamento de erros (B11) atravessando os handlers, com testes cobrindo os quatro pontos de B12 em `tests/`.
7. Escrever `template.yaml` do SAM provisionando: `HttpApi`, `Function` (Python 3.12), tabela DynamoDB `SleBridgeThreads`, três segredos no Secrets Manager (referenciados, não criados aqui), IAM policy de leitura restrita aos três segredos + escrita/leitura da tabela.
8. Registrar o Slack app real (B1), provisionar os segredos no Secrets Manager (B10), rodar `sam deploy`, apontar o Events API do Slack para a URL do API Gateway resultante.
9. Executar exemplo end-to-end contra repo teste e registrar em `docs/exemplo-end-to-end.md` (B14).

## Perguntas em aberto
nenhuma.
