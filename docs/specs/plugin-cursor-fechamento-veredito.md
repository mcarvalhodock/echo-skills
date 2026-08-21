# plugin-cursor-fechamento — veredito

Medido contra o diff `f436348..HEAD` limitado a `.`, no repositório `C:\dock-codes\echo-skills`.
Evidência: diff de `docs/specs/plugin-cursor.md` (arquivo novo com M14 e M15) e diff de
`docs/specs/plugin-cursor-manual-validation.md` (arquivo novo com os marcadores `spec:M14`
e `spec:M15` e a linha de evidência humana).

- **F1** — atendido
- **F2** — atendido
- **F3** — atendido

## Por quê

**F1.** O diff adiciona `docs/specs/plugin-cursor.md` com M14 e M15 na forma:

> **M14** `integração` — Com o pacote carregado, o painel **Customize → Skills** do Cursor lista as seis skills (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`, `prototipar-frontend`) vindas do plugin `sle`.
>
> **M15** `integração` — Com o pacote carregado, o painel **Customize → Agents** do Cursor lista as três definições de agente (`sle-codificar`, `sle-verificar`, `sle-homologar`) vindas do plugin `sle`.

As duas linhas medem efeito — "o painel … lista" — e não nomeiam mecanismo de carga:
não aparece `~/.cursor/plugins/local`, nem `--plugin-dir`, nem `marketplace`, nem equivalente.
Onde a spec fala de mecanismo, ela o joga para o "Contrato técnico" (`A doc do Cursor não descreve…`)
e para o "Plano" (`Carregar em ~/.cursor/plugins/local`), não para o critério. É exatamente o que
F1 cobra.

**F2.** O diff adiciona `docs/specs/plugin-cursor-manual-validation.md` com o marcador `spec:M14`
e o texto:

> **spec:M14** — as seis skills (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`,
> `prototipar-frontend`) aparecem em **Customize → Skills** vindas do plugin `sle`.
> **Estado: atendido em 2026-08-21.** Observação humana em nova janela do Cursor após o reload:
> as seis skills apareceram em **Customize → Skills** vindas do plugin `sle`, na descrição esperada.
> Contagem: seis presentes.

A "observação humana pendente" que a intenção da spec de fechamento nomeia foi substituída pela
linha de evidência com data, contagem e sessão. O marcador `spec:M14` está presente, no formato
que o contrato técnico exige. É o registro que F2 pede.

**F3.** Mesmo arquivo, marcador `spec:M15` presente, com as três definições nomeadas e a linha
de evidência:

> **spec:M15** — as três definições de agente (`sle-codificar`, `sle-verificar`, `sle-homologar`)
> aparecem em **Customize → Agents** vindas do plugin `sle`.
> **Estado: atendido em 2026-08-21.** Observação humana na mesma sessão de M14: as três definições
> apareceram em **Customize → Agents** vindas do plugin `sle`, na descrição esperada. Contagem: três
> presentes.

Os três nomes de agente batem com o critério (`sle-codificar`, `sle-verificar`, `sle-homologar`);
a contagem "três presentes" bate; o marcador `spec:M15` está no formato exigido; a linha "pendente
de observação humana" foi substituída pela evidência. É o registro que F3 pede.
