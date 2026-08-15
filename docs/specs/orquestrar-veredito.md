# Veredito — orquestrar

**Escopo verificado.** `git diff 88ffde8..HEAD -- .` retorna vazio: `88ffde8` **é** o HEAD atual. Todo o trabalho desta demanda está no índice, não commitado — `git diff --name-status HEAD` mostra `A docs/specs/orquestrar.md` e `A orquestrar/SKILL.md`. O veredito foi lavrado contra esses dois arquivos como estão na árvore. Nada além deles foi lido.

## Critérios

- **O1** — atendido
- **O2** — atendido
- **O3** — atendido
- **O4** — atendido
- **O5** — atendido
- **O6** — atendido
- **O7** — atendido
- **O8** — atendido
- **O9** — atendido
- **O10** — atendido
- **O11** — atendido
- **O12** — atendido
- **O13** — atendido
- **O14** — atendido

## Porquê

**O1** — `orquestrar/SKILL.md` existe e abre com frontmatter delimitado por `---` contendo exatamente os três campos que o critério nomeia: `name: orquestrar` (linha 2), `description` (linha 3) e `disable-model-invocation: false` (linha 4). Ressalva de método: o critério diz "no mesmo formato das outras skills", e a comparação com os arquivos vizinhos não foi feita porque a instrução deste veredito proibiu ler qualquer outra coisa. O que foi conferido é a lista de campos que o próprio critério enumera — e essa parte está satisfeita.

**O2** — A `description` traz a cláusula de recusa iniciada literalmente por "NÃO use": *"NÃO use antes de haver spec aprovada, nem para escrever a spec — isso é de `especificar`, e ele roda antes e fora daqui."* (linha 3).

**O3** — Duas afirmações separadas, ambas presentes. A linha 13: "**A orquestração começa depois de uma spec aprovada no gate.** Antes disso não há o que conduzir." E a linha 15: "**Você não despacha `especificar`.**", com a razão anexada — o contrato precede a construção, e spec escrita por quem conduz a implementação vira descrição.

**O4** — Linha 17 declara "Três fases rodam **fora de você, em contexto isolado**" e as lista nominalmente: `codificar`, `verificar`, `homologar` (linhas 19–21). A linha 23 ainda define o que "isolado" quer dizer — a fase não vê esta sessão.

**O5** — A tabela das linhas 31–35 nomeia, fase a fase, o que atravessa: `codificar` recebe caminho da spec aprovada e alvo; `verificar` recebe caminho da spec, ref base do diff, escopo e alvo; `homologar` recebe as specs do ciclo com seus vereditos, o ref base do ciclo e o alvo. A linha 37 ainda distingue o ref base do ciclo do ref da última demanda, que era a confusão que o critério existia para prevenir.

**O6** — Linha 27: "**Nada da conversa atravessa.** O que passa é artefato em arquivo, e só." Seguido da consequência operacional — o que não está escrito não chega do outro lado, e a resposta é escrever, não explicar na chamada.

**O7** — Linha 43: "**Você não escreve código de produção e não escreve teste.** Nem 'só uma linha', nem 'enquanto o `codificar` não volta'." É proibição em texto, como a spec exigia; a linha 45 confirma explicitamente que não há hook nem bloqueio e que isso é deliberado, o que fecha com a linha de "Fora de escopo" da spec em vez de contradizê-la.

**O8** — Tabela nas linhas 51–55 com as três classificações e um destino cada: `atendido` → segue; `não atendido` → volta para `codificar`; `não verificável` → sobe para o humano. A linha 57 justifica o terceiro destino como defeito de spec e não de código.

**O9** — Linha 61: "**Aprovada a spec no gate, você despacha `codificar` e, quando ela termina, `verificar` — sem intervenção humana entre as duas.**" A frase seguinte fecha a brecha mais provável, nomeando "posso seguir?" entre as fases como parada indevida.

**O10** — Linha 63 afirma que as duas paradas planejadas são as únicas paradas humanas previstas, nomeando-as (gate da spec e homologação). A linha 65 declara qualquer outra parada como exceção que "precisa de motivo nomeado", e enumera as duas exceções vigentes: critério `não verificável` e insumo que falta. O critério pedia a afirmação; o arquivo entrega a afirmação mais a lista fechada, o que é mais forte, não menos.

**O11** — A seção das linhas 82–88 é dedicada a isso. Linha 84 fixa que o arquivo define o que é isolado e o que atravessa, não a ferramenta; linha 86 dá o caso degradado explícito — "abra uma sessão nova à mão e entregue os insumos da tabela — o contrato é o mesmo" — e ecoa o "duas pessoas e um editor de texto" de `metodologia-sle.md:124` que o contrato técnico citava.

**O12** — Varredura do arquivo inteiro: nenhum harness, CLI, produto ou ferramenta aparece nomeado. As únicas entidades citadas são skills do próprio método (`especificar`, `codificar`, `verificar`, `homologar`) e conceitos ("contexto isolado", "sessão nova"). A linha 88 ainda diz em texto que nenhuma ferramenta é obrigatória, com a razão — amarrar uma quebraria o método onde ela não existe.

**O13** — Linha 74: "**Você termina devolvendo a demanda ao humano, para a homologação.**", seguida da negativa complementar — "Você não homologa" — e do motivo (o verde autoatestado que a segunda invariante corta). O diagrama da linha 79 termina em `┤homologação├`, consistente.

**O14** — Linha 76: "**Havendo mais de uma spec aprovada, o par `codificar`→`verificar` se repete por spec.** Não se reespecifica". O diagrama `(codificar → verificar) × N` na linha 79 representa a repetição, e a justificativa amarra à primeira invariante.

## Observação de escopo

O checklist "Antes de devolver" (linhas 90–97) não é exigido por nenhum critério, mas nenhum de seus itens contradiz o corpo: cada linha espelha um critério já verificado acima.
