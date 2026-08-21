# plugin-cursor-fechamento

## Intenção
`plugin-cursor` fecha 15/15: M14 e M15 passam a medir **o que aparece no painel do Cursor** em vez de nomear o mecanismo de carga, e a observação humana pendente é executada e registrada.

## Depende de
- `versao-limpa-das-skills`
- `plugin-cursor`

## Critérios
- [ ] **F1** `integração` — O texto de M14 e M15 em `docs/specs/plugin-cursor.md` mede efeito — o que aparece no painel do Cursor — sem nomear mecanismo de carga (`~/.cursor/plugins/local`, `--plugin-dir`, marketplace ou equivalente).
- [ ] **F2** `integração` — Com o pacote carregado, o painel **Customize → Skills** do Cursor lista as seis skills (`especificar`, `codificar`, `verificar`, `homologar`, `orquestrar`, `prototipar-frontend`) vindas do plugin `sle`.
- [ ] **F3** `integração` — Com o pacote carregado, o painel **Customize → Agents** do Cursor lista as três definições (`sle-codificar`, `sle-verificar`, `sle-homologar`) vindas do plugin `sle`.

## Contrato técnico
- F1 corrige defeito de spec já diagnosticado em `pedidos.md` — "critério que nomeia o instrumento envelhece junto com ele". A redação nova das duas linhas se alinha ao que `docs/specs/plugin-cursor-manual-validation.md` já mede.
- F2 e F3 são validação manual, registradas em `docs/specs/plugin-cursor-manual-validation.md` com marcadores `spec:M14` e `spec:M15` (o formato que `tooling/ci/criterion-coverage.yml` exige). O arquivo já traz o procedimento de carga; o que falta é a linha de evidência substituindo "pendente de observação humana".
- O instrumento de carga fica no plano, não no critério. Hoje o procedimento documentado é junção em `~/.cursor/plugins/local/sle`; se o Cursor mudar isso, os critérios não mudam.
- Nada além do padrão do repositório.

## Fora de escopo
- Publicar o pacote no marketplace do time — depende de admin e plano do Cursor; spec própria.
- Confirmar a carga em Cloud Agent — só observável depois de publicado; spec própria.
- Alterar `.cursor-plugin/plugin.json` — o pacote já foi provado como estrutura correta (M1–M13 verdes).
- Regenerar `docs/specs/plugin-cursor-veredito.md` — é artefato de `verificar`; sai naturalmente quando o ciclo rodar contra `plugin-cursor` outra vez, se você quiser o novo carimbo formal.

## Plano
1. Trazer `demanda/versao-limpa-das-skills` para `main` e rebasear `demanda/plugin-cursor` sobre `main`, para as skills limpas e o pacote coexistirem na mesma árvore.
2. Reescrever M14 e M15 em `docs/specs/plugin-cursor.md` medindo efeito (F1).
3. Executar o procedimento já documentado em `docs/specs/plugin-cursor-manual-validation.md` (junção → **Developer: Reload Window** no Cursor → observar **Customize → Skills** e **Customize → Agents**).
4. Substituir "pendente de observação humana" pelas duas linhas de evidência em `docs/specs/plugin-cursor-manual-validation.md`, mantendo os marcadores `spec:M14` e `spec:M15` (F2, F3).

## Perguntas em aberto
nenhuma.
