# orquestrar-lote

## Intenção
Diante de um lote de specs, o orquestrador decide sozinho o que é corrigível e segue, e para só no que exige o humano — em vez de devolver cada transição para ele.

## Depende de
`orquestrar`

## Critérios

- [ ] **L1** `miolo` — `orquestrar/SKILL.md` declara que, ao receber um lote aprovado, o orquestrador lê todas as specs antes de despachar a primeira.
- [ ] **L2** `miolo` — A skill define divergência como par de critérios, de specs diferentes, que incidem sobre o mesmo ponto do código.
- [ ] **L3** `miolo` — A skill dá o teste que classifica a divergência: existe implementação que atenda os dois critérios?
- [ ] **L4** `miolo` — Havendo implementação que atenda os dois, o orquestrador prossegue e registra qual é.
- [ ] **L5** `miolo` — Não havendo nenhuma, o orquestrador para e sobe para o humano.
- [ ] **L6** `miolo` — Ao parar por divergência, o orquestrador nomeia as duas specs e o par de critérios.
- [ ] **L7** `miolo` — A skill declara que a leitura do lote só alcança contradição escrita nas specs, e não substitui o veredito de cada demanda.
- [ ] **L8** `miolo` — A skill declara parada quando a decisão depende exclusivamente do humano, e dá o teste que separa esse caso do corrigível.
- [ ] **L9** `miolo` — O que é corrigível prossegue sem parar, com a recomendação registrada.
- [ ] **L10** `miolo` — Ao prosseguir, o orquestrador despacha a fase correspondente ao tipo do problema, e a skill dá o mapa problema→fase.
- [ ] **L11** `miolo` — O teto é de **duas** tentativas por critério `não atendido`; a segunda reprovação para e sobe para o humano.
- [ ] **L12** `miolo` — A skill reproduz as três exceções de `metodologia-sle.md:114` — `não verificável`, teto estourado e insumo faltante — como paradas, sem inventar outras.
- [ ] **L13** `miolo` — Spec bloqueada por insumo entra em quarentena junto com as que dependem dela, e o resto do lote segue.
- [ ] **L14** `plataforma` — `metodologia-sle.md` nomeia a divergência entre specs junto das outras exceções de parada.

## Contrato técnico

**Divergência não é parada; é bifurcação.** Duas specs tocarem o mesmo ponto do código é o caso comum num lote, e quase sempre existe implementação que atende as duas — aí não há contradição, há tensão aparente, e parar nela devolveria ao humano exatamente o trabalho que o orquestrador existe para absorver. Contradição real é o caso em que **nenhuma** implementação atende os dois critérios: atender um necessariamente reprova o outro. **L3** é o teste que separa, e é o critério que carrega esta spec — sem ele, "divergência" vira rótulo para qualquer desconforto e o lote para o tempo todo.

Isso torna a divergência um caso particular da regra de **L8**/**L9**, não uma exceção paralela: resolvível é corrigível e segue; irresolvível é decisório e sobe.

**A divergência é a única exceção nova.** `metodologia-sle.md:114` já fixa as outras três — `não verificável`, teto estourado, insumo faltante — e a quarentena que as acompanha. **L12** e **L13** reproduzem o que já está escrito, no ponto onde a decisão é tomada; **L15** acrescenta a divergência à lista canônica. Inventar exceção fora dessas quatro é o que transforma "para quando precisa" em "para sempre que tem dúvida", que é o defeito que fez o loop anterior engessar.

**L7 existe para a leitura do lote não virar promessa.** Ler as specs pega contradição *declarada*. A que só aparece no código não é alcançável ali, e a rede para ela continua sendo o veredito de cada demanda. Sem esse limite escrito, a leitura prévia é lida como garantia de que o lote é coerente.

**O teste de L8 é o mesmo da régua de `especificar`:** se prosseguir exigiria *supor* algo sobre a intenção de alguém — preferência, prioridade, apetite de risco —, para. Se a resposta é derivável do codebase, do manifesto ou das specs, é corrigível e segue. A régua já existe no método; **L8** a aplica à decisão de conduzir, e não a duplica.

Duas é o teto de **L11** porque é o menor número que distingue erro de implementação de critério ambíguo: a primeira reprovação pode ser código, a segunda pelo mesmo motivo raramente é. Por isso a segunda sobe como suspeita de spec ambígua, não como código ruim.

Esta spec não cria artefato novo: ela acrescenta seções a `orquestrar/SKILL.md`, que nasce na spec de que esta depende.

## Fora de escopo

- **Detecção de divergência durante o lote**, quando ela só aparece no código. Decisão do humano no gate: a leitura é prévia. **L7** declara o limite em vez de escondê-lo.
- **Rodar o lote sem o gate humano no fim.** As duas paradas planejadas continuam; o guarda é o **O10** de `orquestrar`, e não se repete aqui.
- **Retomar lote interrompido no meio.** Sem histórico de execução não há ponto de retomada, e o histórico era do loop removido.
- **Reconciliar contradição real.** Quando nenhuma implementação atende os dois critérios, o orquestrador nomeia o par e para — reescrever uma das specs é decisão de quem as aprovou. Resolver a divergência *resolvível* não está fora de escopo: é o **L4**.
- **Teto de tentativas configurável.** Dois é número do método, não parâmetro — configurável, viraria a primeira coisa que alguém aumenta para não ser interrompido.

## Plano

1. **`orquestrar/SKILL.md`** — seção de leitura do lote, com a definição, o teste e os dois desfechos (L1–L7); seção de condução, com o teste do que sobe e o mapa problema→fase (L8, L9, L10); seção de paradas por exceção, com o teto (L11–L14).
2. **`metodologia-sle.md`** — a divergência entra na lista de exceções de `:114` (L15).

Não é fatiável. Quatorze dos quinze critérios são `miolo` e caem no mesmo arquivo; o único de `plataforma` é uma linha que só faz sentido depois que o comportamento existe.

## Perguntas em aberto

Vazio.
