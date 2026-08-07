# Manifesto ECHO — echo-skills (alias legado)

> **Este arquivo é um alias legado.** O manifesto ativo do repositório vive em [`.sle/manifesto.md`](../.sle/manifesto.md) desde a refatoração ECHO → SLE (2026-08-07). As skills leem `.sle/` primeiro; se ausente, caem para este arquivo como fallback.
>
> Este arquivo permanece por dois motivos:
> 1. Compatibilidade com repositórios consumidores que ainda não migraram para `.sle/`.
> 2. Documentar o histórico do método (o ECHO existiu antes do SLE; o conteúdo abaixo é o manifesto ECHO original).
>
> Se você está criando um manifesto novo em um repositório, use `.sle/manifesto.md`. Este aqui é referência histórica.

---

# Manifesto ECHO — versão original (histórica)

> Formato e regras em [`dominios.md`](../dominios.md). Este arquivo é a declaração real deste repositório, não um exemplo — o exemplo de preenchimento vive no catálogo.

## Domínios ativos

**Nenhum.**

Isto é uma declaração, não uma pendência. `echo-skills` é um repositório de metodologia: markdown, sem código de aplicação, sem runtime, sem dado. Toda mudança aqui é regra de negócio do próprio método — `miolo`, na classificação do catálogo.

A consequência é útil e foi verificada na prática: specs deste repositório não fatiam, porque falham na condição de **pluralidade**. A primeira spec a usar este manifesto foi a da própria decomposição por domínio, e ela se classificou como 100% miolo. Um desenho errado teria inventado domínios para justificar a si mesmo.

## Domínios inativos

| domínio | por quê |
|---|---|
| `segurança` | não há authn, autorização ou segredo — o repositório é público por natureza |
| `privacidade` | não trata dado pessoal de ninguém |
| `dados` | não há schema, migração ou persistência |
| `integração` | não expõe nem consome API |
| `plataforma` | não há deploy, runtime ou ambiente a provisionar |
| `experiência` | não há interface; o consumo é por leitura de markdown e invocação de skill |

## Donos

Não se aplica — repositório de uso pessoal. Ver [`propostas/expansao-para-times.md`](../propostas/expansao-para-times.md) para o raciocínio sobre aprovador nomeado por domínio, que segue como hipótese não validada.

## Quando este manifesto muda

Se o método ganhar componente executável — um hook de enforcement, um CLI, uma automação de CI — `plataforma` e `integração` deixam de ser inativos. Até lá, revisar isto seria inventar necessidade.

**Nota histórica (2026-08-07):** essa condição *aconteceu* — o método SLE, sucessor do ECHO, ganhou componente executável (hooks, CI). O manifesto ativo agora é `.sle/manifesto.md`, e lá `plataforma` e `integração` estão ativos.
