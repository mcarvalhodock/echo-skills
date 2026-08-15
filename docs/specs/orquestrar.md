# orquestrar

## Intenção
O chat que conversa com o humano deixa de codificar: ele recebe spec pronta e orquestra a construção dela, despachando `codificar` e `verificar` para contexto isolado até devolver a demanda para homologação.

## Depende de
Nenhuma.

## Critérios

- [ ] **O1** `miolo` — Existe `orquestrar/SKILL.md` com frontmatter no mesmo formato das outras skills: `name`, `description`, `disable-model-invocation: false`.
- [ ] **O2** `miolo` — A `description` contém cláusula de recusa iniciada por "NÃO use".
- [ ] **O3** `miolo` — A skill declara que a orquestração começa depois de uma spec aprovada no gate, e que `especificar` não é despachado por ela.
- [ ] **O4** `miolo` — A skill declara que `codificar`, `verificar` e `homologar` rodam fora do orquestrador, em contexto isolado.
- [ ] **O5** `miolo` — A skill nomeia, para cada uma das três fases isoladas, os insumos que atravessam a fronteira.
- [ ] **O6** `miolo` — A skill afirma que nada da conversa atravessa a fronteira: o que passa é artefato em arquivo.
- [ ] **O7** `miolo` — A skill proíbe, em texto, que o orquestrador escreva código de produção ou teste.
- [ ] **O8** `miolo` — A skill traz a tabela de roteamento por classificação do veredito: `atendido`, `não atendido` e `não verificável`, cada uma com o destino.
- [ ] **O9** `miolo` — Aprovada a spec no gate, o orquestrador despacha `codificar` e depois `verificar` sem intervenção humana entre as duas.
- [ ] **O10** `miolo` — A skill afirma que as duas paradas planejadas do ciclo são as únicas paradas humanas previstas, e que o resto é exceção.
- [ ] **O11** `miolo` — A skill afirma que o isolamento é o contrato e o mecanismo é acessório: sem subagente, abre-se sessão à mão, e o contrato é o mesmo.
- [ ] **O12** `miolo` — A skill não nomeia nenhum harness ou ferramenta como obrigatório.
- [ ] **O13** `miolo` — A skill declara que a orquestração termina devolvendo a demanda ao humano, para a homologação.
- [ ] **O14** `miolo` — Havendo mais de uma spec aprovada, o par `codificar`→`verificar` se repete por spec, sem reespecificar.

## Contrato técnico

**O contrato de isolamento é agnóstico; a ligação é acessória.** `metodologia-sle.md:124` afirma que o método roda "em qualquer harness que saiba abrir uma sessão limpa — e, no limite, com duas pessoas e um editor de texto". **O12** é o guarda dessa afirmação: `orquestrar/SKILL.md` descreve *o que* é isolado e *o que* atravessa, nunca *com que ferramenta*. A ligação concreta é de `orquestrar-ligacao`, e é substituível sem tocar no contrato — mesmo padrão da escada de `prototipar-frontend`.

**`especificar` é independente da orquestração, e isso é fronteira, não sequência.** O orquestrador nunca o despacha: ele começa a existir quando já há spec aprovada. A razão é a invariante 1 de `metodologia-sle.md` — o contrato precede a construção, e uma spec escrita por quem já está conduzindo a implementação deixa de ser contrato e vira descrição. **O14** é a consequência: mais specs não significam reespecificar, significam repetir `codificar`→`verificar` sobre contratos que já existiam antes de qualquer código.

**O13 fixa o ponto de retorno.** A orquestração não fecha o ciclo: ela devolve à homologação humana, que é a segunda das duas paradas planejadas. Orquestrador que se auto-homologa reintroduz o verde autoatestado que a invariante 2 existe para cortar.

**O9 não é evolução contra o método: é o método cumprindo o que já afirma.** `metodologia-sle.md:114` diz que, fora das duas paradas planejadas, só se interrompe por exceção. O que foi removido em `1cfcc86` foi o CLI que encadeava, não o princípio de encadear — e enquanto ninguém ocupa esse lugar, cada transição vira uma pergunta ao humano que o método nunca previu. **O10** fixa o outro lado: parada humana fora das duas planejadas é exceção, e exceção precisa de motivo.

**O5 é o critério que carrega a demanda.** Isolamento sem insumo declarado não é isolamento: é uma fase que não recebe o que precisa e reinventa por conta. Os insumos de cada fase já estão escritos na seção "Insumos" de `codificar/SKILL.md`, `verificar/SKILL.md` e `homologar/SKILL.md` — **O5** os reúne no ponto de despacho, não os inventa.

**Receber spec pronta é a natureza do orquestrador, não uma restrição de escopo desta spec.** Ele orquestra a construção do que já foi contratado — uma spec por padrão, e lotes depois, quando `orquestrar-lote` fechar. A escala muda; a natureza não. Por isso **O3** é critério e não linha de "Fora de escopo": um orquestrador que escrevesse spec seria outra coisa.

`metodologia-sle.md:16` e `codificar/SKILL.md:71` citam "o roteador" como quem encadeia as fases. Ele era `tooling/loop/`, removido em `1cfcc86`: hoje as duas linhas apontam para algo que não existe. Quem as corrige é o **G3** de `orquestrar-ligacao` — fica registrado aqui porque é esta demanda que cria o papel que aquelas linhas passarão a nomear.

O orquestrador **não** é fase do ciclo, e não entra na tabela de `metodologia-sle.md`. Ele é quem chama as fases; virar linha da tabela o tornaria fase de si mesmo.

## Fora de escopo

- **Hook, marker-file ou bloqueio que impeça o orquestrador de editar código.** `metodologia-sle.md:22` já registra que essas defesas custaram mais do que protegiam. **O7** é texto, e é deliberado que seja.
- **Automatizar o gate humano.** As duas paradas por ciclo continuam humanas; um orquestrador que aprova a própria spec elimina a invariante que o método existe para proteger.
- **Condução de lote** — decidir se continua ou para diante de N specs. Fica para `orquestrar-lote`, que depende desta: sem a fronteira e a tabela de roteamento definidas aqui, não há o que conduzir. Esta spec despacha uma fase por vez.
- **`prototipar-frontend`.** Acessória, roda antes do ciclo, e o orquestrador não a despacha.
- **Retomada de sessão isolada que falhou no meio.** Sem histórico de execução, não há o que retomar — e o histórico era do loop.

## Plano

1. **`orquestrar/SKILL.md`** — frontmatter (O1, O2), depois o corpo na ordem do fluxo: onde a orquestração começa e o que roda fora (O3, O4), a fronteira e seus insumos (O5, O6), a proibição (O7), o roteamento por veredito (O8), o despacho automático e as paradas (O9, O10), onde termina e o que se repete (O13, O14), mecanismo acessório (O11, O12).

Um arquivo, quatorze critérios `miolo`. Não é fatiável: a ligação com o harness e a instalação saíram para `orquestrar-ligacao`, porque somar os critérios de despacho automático estourava o teto — e spec no teto não recebe emenda, recebe divisão.

## Perguntas em aberto

Vazio.
