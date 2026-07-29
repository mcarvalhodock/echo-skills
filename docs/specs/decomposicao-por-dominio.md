# Spec: Decomposição por domínio na Fase E/C do ECHO (v2)

> Nível 3 — mudança arquitetural no método. Substitui a v1 (branch `experimento/decomposicao-por-dominio`), que tratava domínio como taxonomia do trabalho e acoplava fatiamento ao nível de risco.

## Intenção
A spec passa a marcar cada critério de aceite com o domínio que o endereça, e o plano passa a decidir — por condições próprias, independentes do nível de risco — se aquela demanda se fatia em sub-specs descartáveis executáveis por especialistas, humanos ou subagentes.

## Contexto
A v1 tratou domínio como taxonomia do trabalho, com catálogo fechado inventado no papel e fatiamento acoplado ao nível N2/N3. Duas correções: domínio é **endereço de roteamento** (deriva dos especialistas que existem, não de uma ontologia), e fatiabilidade é eixo distinto de risco. Sem a Fase C consumindo a marcação, ela não passa de preenchimento de campo.

## Domínios envolvidos
Nenhum. Esta mudança é 100% miolo — regra de negócio do próprio método, em markdown. **E isso é o primeiro teste do gatilho: falta pluralidade, então não fatia.** Se o desenho estivesse errado, ele inventaria domínios aqui para justificar a si mesmo.

## Critérios de aceite

### Camada 1 — vocabulário canônico
- [ ] `dominios.md` na raiz documenta exatamente 6 domínios: `segurança`, `privacidade`, `dados`, `integração`, `plataforma`, `experiência`
- [ ] Cada domínio tem nome, o que endereça, especialista típico e ao menos um exemplo de critério que lhe pertence
- [ ] A fronteira `segurança`/`privacidade` está documentada com o teste de discriminação (um sistema seguro pode ser ilegal)
- [ ] Retenção aparece sob `privacidade` (prazo legal e descarte), e o ciclo de vida técnico sob `dados` — sem sobreposição
- [ ] As tensões declaradas (`plataforma` largo; `performance` pode se emancipar; observabilidade pode se emancipar) estão registradas como texto, não como TODO
- [ ] `dominios.md` é fonte única: template e skills referenciam, nunca duplicam a lista

### Camada 2 — ativação local
- [ ] `.echo/manifesto.md` tem formato documentado com: domínios ativos, quais são obrigatórios, ferramental por domínio, e dívida declarada quando não há ferramental
- [ ] Existe um manifesto real preenchido no próprio `echo-skills`
- [ ] `especificar` lê o manifesto quando existe e restringe as opções aos domínios ativos
- [ ] Sem manifesto, a skill usa o catálogo inteiro e avisa **uma vez** que ele está ausente — não bloqueia
- [ ] Ausência de ferramental de observabilidade **não** desativa `plataforma`: vira dívida declarada, e fatias do tipo produzem recomendação em vez de implementação

### Fase E — marcação
- [ ] Template N2 e N3 ganham a seção "Domínios envolvidos"; N1 permanece byte-idêntico
- [ ] Cada critério de aceite e caso de borda recebe uma de três classificações: domínio(s), **cross-cutting retido**, ou **miolo**
- [ ] `miolo` é classificação válida e esperada — é o que não se delega, não um erro de preenchimento
- [ ] Cross-cutting marca a fatia como retida pelo orquestrador, não como delegável a vários
- [ ] A skill recusa domínio fora do catálogo/manifesto e oferece a lista canônica
- [ ] Toda recusa é gravada em `.echo/pressao-catalogo.md` com data, spec, nome tentado e o que se queria expressar
- [ ] A regra de fechamento cobre a seção nova: nenhuma spec pronta com item sem classificação

### Fase C — fatiamento
- [ ] `planejar` avalia três condições — **pluralidade**, **independência**, **massa** — e declara fatiável ou não, com justificativa escrita
- [ ] O nível de risco (N1/N2/N3) **não** é entrada na decisão de fatiar
- [ ] Não fatiável → o plano sai no formato atual, sem menção a subagente
- [ ] Fatiável → `planejar` propõe as fatias e o usuário aprova antes de qualquer dispatch
- [ ] Sub-spec é gerada **fora do repositório de trabalho**, em `~/.echo/fatias/<repositório>/<spec>/`, com fallback para diretório temporário do sistema quando `HOME` não for gravável
- [ ] Nenhuma skill escreve sub-spec dentro do workspace do cliente, e nenhuma skill edita o `.gitignore` de repositório de terceiro
- [ ] `.echo/manifesto.md` e `.echo/pressao-catalogo.md` continuam sendo criados **dentro** do repositório de trabalho — são declarações do projeto e devem ser versionados por quem o mantém
- [ ] Sub-spec carrega intenção, critérios e casos de borda do domínio, **mais restrições, fora de escopo e ambiente integrais** (o não-fatiável viaja junto)
- [ ] Sub-spec é read-only para o executor: descoberta que altera contrato volta para a spec-mãe
- [ ] O retorno de cada fatia tem dois campos: resultado e **o que a mãe não previu**
- [ ] Remontagem é reconciliação contra os critérios da mãe, nunca união dos outputs
- [ ] "Pronto" do conjunto = critérios da mãe verificados, não "todas as fatias concluídas"

## Casos de borda considerados
- Demanda mono-domínio profunda (refactor arquitetural) — marca 1 domínio, não fatia: falta pluralidade.
- Demanda com 4 domínios rasos — fatia mesmo sendo N2: risco não é o gatilho.
- Todos os critérios classificados como `miolo` — válido, não fatia, e a seção fica registrando isso.
- Domínio ativo no manifesto sem nenhum critério apontando pra ele — sinal de decomposição vaga, skill pede refino.
- Fatia depende de outra (segurança precisa do modelo de dados pronto) — falha em **independência**, não fatia.
- Especialista devolve descoberta que invalida critério da mãe — mãe é atualizada e as fatias afetadas são reemitidas, não remendadas.
- Repo sem manifesto — funciona com catálogo cheio, degradado mas não travado.
- Repositório de cliente com `.gitignore` gerenciado por template ou por outra equipe — a skill não o edita em nenhuma hipótese; a sanitização não depende dele.
- `HOME` não gravável (CI, container) — a geração cai para o diretório temporário do sistema, nunca para dentro do workspace.
- Sub-spec sobrevivendo entre sessões em `~/.echo/fatias/` — é aceito: descartável significa "não versionado", não "apagado imediatamente". A pasta é limpável a qualquer momento sem efeito sobre o método.

## Fora de escopo
- Multi-repo: eixo repositório, matriz disciplina × repo, sequenciamento por dependência de contrato, homologação distribuída.
- Alteração em `homologar/SKILL.md` — a costura contra a spec-mãe existe justamente para mantê-la intacta.
- Bounded context de negócio (pagamentos, cobrança, antifraude) — segundo eixo, depende da empresa, não se inventa no papel.
- Aprovador nomeado por domínio — segue em `propostas/expansao-para-times.md`.
- Nomear executor concreto na spec (ex: `@security-agent`) — spec nomeia domínio, nunca executor.
- Skill da Fase O e enforcement por hook.
- Migração de specs antigas — a seção é aditiva.

## Restrições
- 100% markdown, zero dependência nova.
- Fonte única de verdade para o catálogo; duplicação é defeito.
- Compatibilidade retroativa: specs sem a seção continuam válidas.
- N1 intocado — a válvula de escape do método não pode engordar.
- Legibilidade preservada: seção separada, sem tag inline poluindo critérios.
- A regra de fechamento continua sendo o princípio norteador.

## Ambiente / destino
- Repositório: `C:\dock-codes\echo-skills`.
- Branch: `experimento/decomposicao-por-dominio-v2`, criada a partir de `main`.
- Arquivos criados: `dominios.md`, `.echo/manifesto.md`, `.echo/pressao-catalogo.md`, `.gitignore`.
- Arquivos alterados: `especificar/SKILL.md`, `planejar/SKILL.md`, `template-especificacao.md`, `metodologia-echo.md` (nota curta), `README.md` (árvore de arquivos).
- Spec salva em `docs/specs/decomposicao-por-dominio.md`, **substituindo a v1**.
- `.gitignore` ignora `.echo/fatias/` e preserva manifesto e log de pressão. Com a sub-spec vivendo fora do repositório, essa entrada passa a ser cinto de segurança — cobre quem apontar a geração para dentro do workspace por engano — e não o mecanismo principal de sanitização.
- Sub-specs geradas em `~/.echo/fatias/<repositório>/<spec>/`, fora de qualquer workspace. Fallback para o diretório temporário do sistema quando `HOME` não for gravável (CI, container).
- Skills em `~/.claude/skills/` foram **promovidas deliberadamente** em 2026-07-29, durante a Fase H, para permitir os testes comportamentais — que são impossíveis com a versão anterior instalada. O isolamento original (repo testado sem afetar o fluxo em uso) foi revogado conscientemente, com backup das versões anteriores. Risco aceito e explícito: o fluxo de trabalho em uso passa a rodar a versão experimental enquanto ela estiver em validação.
- Branch v1 preservada intacta como registro; `main` intocada até decisão explícita de promover.

## Nível de risco
- [x] Difícil de reverter em tese (arquitetura do método, agora em duas fases), mitigado por viver em branch. Escala mantida em Nível 3 pela natureza da decisão, não pelo custo técnico de desfazer.

## Alternativas consideradas
1. **Catálogo único global, sem ativação local** (desenho da v1) — descartada: `ux` aparecendo em repo sem frontend é ruído, e "quais especialistas acionar" volta a ser inferência.
2. **Catálogo livre por repo** — descartada: mata o vocabulário compartilhado, que é justamente o que torna a marcação roteável entre projetos.
3. **Manter fatiamento acoplado a N2/N3** — descartada: risco e fatiabilidade são eixos independentes; um N3 mono-domínio não se fatia e um N2 plural se fatia bem.
4. **Fatiar na Fase E** — descartada: obriga a decidir delegação antes de existir plano, quando o tamanho real de cada fatia ainda é desconhecido. E marcação é barata mesmo sem fatiamento.
5. **Sub-spec versionada** — descartada: em poucos meses vira dezenas de órfãos contradizendo as specs-mãe.
6. **Sub-spec efêmera só no prompt** — descartada: quando o especialista erra, não há como reconstruir o que ele leu.
7. **Sub-spec dentro do repo, com a skill inserindo a entrada no `.gitignore` do cliente** — descartada por dois motivos: o enforcement volta a ser probabilístico (depende de o modelo lembrar, exatamente a lacuna que a metodologia manda transformar em harness), e a skill passaria a editar arquivo de configuração de repositório de terceiro, frequentemente gerenciado por template ou por outra equipe. Gerar fora do workspace é determinístico por construção: não se ignora o que nunca entrou.

## Dependências e impacto
- `especificar/SKILL.md`: Passo 2 ganha a seção e a leitura do manifesto; Passo 3 estende o gate de fechamento; a recusa passa a escrever no log de pressão.
- `planejar/SKILL.md`: ganha um passo de avaliação de fatiabilidade antes do plano, e o protocolo de projeção/retorno/reconciliação quando fatiável.
- `template-especificacao.md`: seção nova em N2/N3; o catálogo **sai** daqui e vira `dominios.md`.
- `homologar/SKILL.md`: sem alteração — recebe a spec-mãe como sempre e nem precisa saber que houve fatiamento.
- `metodologia-echo.md` e `README.md`: referências curtas, sem mudança estrutural.
- Uso manual do template fora das skills: nada quebra, a seção pode ficar vazia.

## Plano de verificação
- Rodar `especificar` alterada contra ≥3 tarefas reais: uma mono-domínio, uma plural, uma majoritariamente miolo.
- Rodar `planejar` alterada nas mesmas três e conferir que a decisão de fatiar bate com o julgamento humano — e que as três condições são citadas explicitamente.
- Executar ao menos **uma** demanda fatiada de ponta a ponta, com dispatch real, e verificar que a reconciliação contra a mãe fecha.
- **Teste de sanitização**: executar um fatiamento em repositório que não seja o `echo-skills` e confirmar que `git status` continua limpo — nenhuma sub-spec no workspace, nenhuma alteração no `.gitignore` do projeto.
- Teste negativo: pedir `compliance` e verificar recusa + linha gravada no log de pressão.
- Teste negativo: pedir fatiamento de demanda que falha em independência e verificar que `planejar` recusa.
- Regressão: gerar spec N1 e confirmar formato idêntico ao atual.
- Regressão: rodar `homologar` numa demanda fatiada e confirmar que ela opera só sobre a mãe.
- Sem suíte automatizada — o método é markdown, verificação é executiva e humana.

## Decisão de reversibilidade
- Tudo em `experimento/decomposicao-por-dominio-v2`; `main` intocada.
- Reversão local: `git checkout main && git branch -D experimento/decomposicao-por-dominio-v2`.
- Reversão remota (se subida): `git push origin --delete experimento/decomposicao-por-dominio-v2`.
- `~/.claude/skills/` **já contém a versão experimental** desde 2026-07-29. Reverter o método em uso exige restaurar o backup das skills anteriores, não apenas trocar de branch — o `git checkout` sozinho não desfaz mais a mudança em voo.
- Reversão parcial possível: a Camada 1 (catálogo + marcação) sobrevive sozinha se o fatiamento em `planejar` se mostrar ruim.

## Perguntas em aberto
- **Critério de promoção ao catálogo**: quantas ocorrências no log de pressão promovem um domínio novo? Número não fixado agora porque seria arbitrário — o próprio log é o instrumento que vai revelar o padrão. Incerteza consciente, com mecanismo de resolução já instalado.
- **Independência é julgável de fora?** A condição depende de saber se duas fatias vão negociar entre si — o que às vezes só aparece durante a execução. Se `planejar` errar sistematicamente aqui, a condição precisa de um sinal mais objetivo que julgamento.
- **`plataforma` aguenta a largura?** Deploy, custo, latência e observabilidade sob um dono só. Aposta assumida; o sinal de falha é fatia de performance aparecendo sem nenhum componente de infra.

---

*Spec gerada pela skill `especificar` (Fase E do método ECHO) em 2026-07-29. Substitui a v1 de 2026-07-28. Próximo passo: skill `planejar`.*
