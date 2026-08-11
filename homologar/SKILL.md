---
name: homologar
description: Use ao FIM do desenvolvimento — quando as demandas já passaram por `verificar` e chegou a hora de fechar o ciclo. Roda a suíte completa e prepara as perguntas de arquitetura para o humano responder. NÃO use por demanda; homologar cada spec com a suíte inteira é o custo que essa separação existe para evitar.
disable-model-invocation: false
---

# Homologar

Fim do desenvolvimento. Duas coisas: a suíte inteira, e as perguntas que só um humano responde.

**Não use isto por demanda.** Cada demanda fecha em `verificar`. Se você está aqui depois de uma spec só, está pagando o preço que a separação existe para evitar.

## Passo 1 — A suíte completa é sua

Rode tudo: unitário, integração, ponta a ponta, formatação, lint. Uma vez, aqui.

**Antes de abrir o código.** O que só a suíte completa pega é quebra **fora** das demandas — um teste antigo reprovando o comportamento novo, uma migração que colide, uma configuração compartilhada que mudou. É real, e é por isso que ela existe; ela não some, ela tem dono.

Reporte número real por suíte: quantos executam, quantos passam, quantos falham. Comparar com a medição anterior é o que mostra se o ciclo andou.

## Passo 2 — O checklist arquitetural

Agora pode ler o código: a suíte já rodou e o resultado está fixado.

Prepare as perguntas com **uma observação concreta cada** — um ponto do código, uma frase, sem julgamento. **Você não responde nenhuma delas.**

```markdown
- Esta decisão segura se o volume triplicar?
  [observação concreta]
- Algum acoplamento novo preocupa a longo prazo?
  [observação concreta]
- A implementação diverge do plano em algum ponto não sinalizado?
  [aponte, ou declare "sem divergência aparente"]
- Há dívida sendo criada conscientemente? Foi registrada?
  [observação concreta]
- Você assinaria embaixo disto como se tivesse escrito à mão?
  (só o humano responde — não observe nada aqui)
```

Observação concreta é "`/cadastro` monta as 5571 cidades a cada requisição, sem cache". Não é "a performance pode ser um problema".

Se o humano quiser pular, avise **uma vez** que isso esvazia a fase, respeite a decisão e siga.

## Passo 3 — Reporte

```markdown
## O que mudou
[uma linha por frente do ciclo]

## O que está vermelho
| suíte | executa | passa | falha |
|---|---|---|---|

## O que precisa da sua decisão
[o checklist, mais o que a suíte expôs]
```

## Quando o ciclo não fecha

Falha fora das demandas é o achado mais valioso desta fase — foi ela que a suíte completa existiu para encontrar. Leve ao humano com a saída real e as três saídas de sempre: corrigir, emendar a spec, ou declarar fora de escopo.

Arquitetura é julgamento humano. Você prepara as perguntas, não as respostas.
