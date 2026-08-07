# Catálogo de domínios — SLE

> Fonte única de verdade. Skills e templates **referenciam** este arquivo; nenhum deles repete a lista. Se a lista aparecer duplicada em outro lugar do repo, isso é defeito, não conveniência.

## O que um domínio é (e o que não é)

Um domínio é um **endereço de roteamento**: ele responde *"qual especialista pega essa fatia"*, humano ou subagente. Ele não descreve o trabalho — quem descreve são os critérios de aceite, e esses são livres.

A consequência prática é a regra de crescimento do catálogo: **um domínio novo nasce quando nasce um especialista novo**, não quando uma tarefa parece diferente das anteriores. Um catálogo derivado de uma ontologia bonita marca coisas que ninguém sabe executar; um catálogo derivado do elenco real marca coisas que têm dono.

Por isso não existe domínio `coding`. Ele seria o "outros" disfarçado — e o que ele tentaria endereçar (a regra de negócio, o comportamento central da demanda) é justamente o que **não se delega**. Esse resto tem nome próprio aqui: `miolo`.

## Duas camadas

O catálogo funciona em duas camadas, com ciclos de vida diferentes:

1. **Vocabulário canônico** — este arquivo. Compartilhado, cresce devagar, por evidência registrada. Garante que `segurança` significa a mesma coisa em qualquer projeto.
2. **Ativação local** — `.sle/manifesto.md` em cada repositório (com `.echo/manifesto.md` como alias legado, lido como fallback se `.sle/` estiver ausente). Declara quais domínios existem *ali*, quais são obrigatórios e qual ferramental está disponível. Muda com o projeto, sem pedir licença ao vocabulário.

Sem essa separação, `experiência` aparece como opção em repo sem frontend, e "quais especialistas acionar" volta a ser inferência — que é exatamente o que o método tenta tirar do caminho.

## Os domínios

| domínio | o que endereça | especialista típico |
|---|---|---|
| `segurança` | autenticação, autorização, segredo, criptografia, superfície de ataque | AppSec |
| `privacidade` | base legal, finalidade, minimização, retenção e descarte, direitos do titular, anonimização | DPO / Privacy |
| `dados` | modelagem, migração, integridade, padrão de consulta e volume | Eng. de dados / DBA |
| `integração` | contrato entre sistemas, API, mensageria, versionamento de interface | Arquiteto / dono do contrato |
| `plataforma` | deploy, ambiente, disponibilidade, custo, latência e escala, observabilidade | SRE / Plataforma |
| `experiência` | interface, fluxo do usuário, acessibilidade, conteúdo | Design / Frontend |

Exemplo de critério que pertence a cada um:

- **`segurança`** — "apenas o próprio titular consegue ler o registro; qualquer outro papel recebe 403"
- **`privacidade`** — "o CPF é descartado 90 dias após o encerramento do contrato, sem intervenção manual"
- **`dados`** — "a migração roda em lote sem lock de tabela e é idempotente se reexecutada"
- **`integração`** — "a v1 do endpoint continua respondendo enquanto a v2 é publicada; nenhum consumidor precisa mudar no mesmo deploy"
- **`plataforma`** — "a rota responde em até 300ms no p95 com o dobro do tráfego atual"
- **`experiência`** — "o formulário é navegável só por teclado e cada erro é anunciado por leitor de tela"

## A fronteira `segurança` / `privacidade`

Os dois existem separados porque respondem a perguntas diferentes:

- **`segurança`** pergunta *"alguém consegue acessar o que não deveria?"* — é sobre proteger o sistema.
- **`privacidade`** pergunta *"temos legitimidade para tratar esse dado, mesmo com acesso autorizado?"* — é sobre o uso ser lícito.

**Teste de discriminação:** um sistema perfeitamente seguro pode ser ilegal. CPF armazenado com criptografia forte e acesso rigorosamente controlado, sem base legal e sem prazo de descarte, é violação de LGPD com segurança impecável. O inverso também vale: dado público mal protegido é falha de segurança sem tocar privacidade.

Se um critério marca os dois, verifique se não são dois critérios diferentes escritos como um só. Marcar ambos por reflexo esvazia o roteamento — o objetivo é chamar o especialista certo, não cobrir-se.

## Retenção: onde ela mora

Retenção aparece nos dois vocabulários e precisa de linha fixa:

- **Prazo legal, base para guardar, obrigação de descartar** → `privacidade`
- **Volume, arquivamento, particionamento, ciclo de vida operacional** → `dados`

"Apagar o dado do titular em 90 dias" é `privacidade`. "Mover registros com mais de 2 anos para tabela fria porque a consulta degradou" é `dados`.

## As três classificações

Todo critério de aceite e todo caso de borda de uma spec N2/N3 recebe **uma** destas classificações:

- **Domínio(s)** — pertence a uma ou mais disciplinas acima e é candidato a delegação.
- **Cross-cutting retido** — toca vários domínios de forma inseparável. **Não se delega**: fatiar produziria leituras parciais da mesma decisão, e alguém teria que reconciliar depois. Fica com o orquestrador.
- **Miolo** — a regra de negócio, o comportamento central. Classificação válida e esperada; fica com quem é dono da demanda.

Uma spec inteiramente classificada como `miolo` é um resultado legítimo, não um erro de preenchimento. Significa que a demanda não tem aspecto delegável — só corpo.

## Manifesto por repositório

Cada repositório declara sua ativação local em `.sle/manifesto.md` (com `.echo/manifesto.md` como alias legado). Formato:

```markdown
# Manifesto SLE — [nome do repositório]

## Domínios ativos
| domínio | obrigatório | ferramental | observações |
|---|---|---|---|
| `segurança` | sim | — | toda spec precisa classificar authn/authz |
| `dados` | não | PostgreSQL 15, Flyway | |
| `plataforma` | não | — | **dívida**: sem ferramental de observabilidade |

## Domínios inativos
- `experiência` — não há interface neste repositório
- `integração` — serviço não expõe nem consome API externa
- `privacidade` — não trata dado pessoal

## Padrão de código local
[STYLE.md / .editorconfig / linter config, ou "boas práticas gerais" quando não declarado]

## tdd-aplicavel
[`ortodoxo` (default) | `parcial` | `manual`]

## Donos
[Quem responde por cada domínio ativo, quando houver nome definido. Opcional.]
```

Regras do manifesto:

- **Manifesto ausente não bloqueia.** A skill avisa uma vez e usa o catálogo canônico inteiro. Funciona degradado, não travado.
- **Domínio inativo precisa de justificativa**, não só ausência. "Não há interface aqui" é informação; silêncio não é.
- **Ausência de ferramental não desativa o domínio — declara uma dívida.** Um repo sem stack de observabilidade não deixa de precisar ser observável. Nesse caso, fatias do domínio produzem **recomendação** em vez de implementação, o que é honesto e ainda útil.
- **Ferramental declarado tem retorno prático imediato:** um especialista que sabe o stack gera instrumentação real; sem saber, gera pseudocódigo genérico que ninguém aproveita.

O que vive em `.sle/` (ou `.echo/` como alias legado) dentro do repositório é só o que **pertence** ao projeto: o manifesto, o log de pressão sobre o catálogo, e o log de pressão sobre o método — todos versionados por quem mantém o repo. Sub-specs geradas pelo fatiamento **não vivem ali** — são artefato de execução e nascem fora de qualquer workspace, para que a sanitização não dependa de um `.gitignore` estar correto em cada cliente. Detalhes na skill `designer` (na seção do Protocolo de fatiamento).

## Como este catálogo evolui

Quando alguém tenta usar um domínio que não existe aqui, a skill **recusa e oferece a lista canônica** — é essa recusa que preserva a precisão no momento da spec. Mas a recusa **grava**: uma linha em `.sle/pressao-catalogo.md` (ou `.echo/pressao-catalogo.md` como alias legado) com data, spec, nome tentado e o que se queria expressar.

Esse log é o instrumento. O critério de promoção de um domínio novo sai da leitura do padrão acumulado — não de um número fixado antes de existir evidência. Uma anotação informal que morre no fim da conversa não serviria: o dado mais valioso do método é a pressão que ele sofre.

## Tensões declaradas

Estas são apostas conscientes, registradas para serem confirmadas ou derrubadas pelo uso — não ressalvas.

**`plataforma` é o domínio mais largo do catálogo.** Comporta deploy, custo, latência, escala e observabilidade. Domínio largo tende a virar o novo "outros". A fusão se sustenta enquanto o especialista for o mesmo, que é o critério deste catálogo — em quase toda empresa de TI, SRE/Plataforma atende os três eixos. **Sinal de falha:** fatias de performance aparecendo sem nenhum componente de infra (otimização algorítmica pura, complexidade de código). Se isso repetir, `performance` volta como domínio próprio.

**Observabilidade está dentro de `plataforma`.** Aposta consciente. Se a Fase Observar ganhar tração real, ela se emancipa — e seria uma emancipação saudável, porque daria dono à fase mais frágil do método (agora conduzida pela skill `observer` no SLE).

**Não existe domínio `qualidade`.** Verificação é a Fase Homologar (conduzida pelo `validator` no SLE), e TDD com testes integrados é default do método, não fatia delegável. Cada domínio verifica a própria fatia. O que se delegaria a um especialista de QA seria a *estratégia* de verificação — se essa necessidade aparecer de forma repetida no log de pressão, a decisão é revista.

**Bounded context de negócio está fora deste catálogo.** `pagamentos`, `cobrança`, `antifraude` são um segundo eixo, ortogonal a este: disciplina roteia *especialista*, bounded context roteia *dono*. Ele depende da estrutura de cada empresa e não se inventa no papel — por isso não está aqui.

---

*Alimenta as Fases Definir e Desenhar do [método SLE](./metodologia-sle.md). Marcação e decisão de fatiar são ambas responsabilidade da skill `designer`.*
