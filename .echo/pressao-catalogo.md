# Log de pressão sobre o catálogo de domínios

> Instrumento de evolução do vocabulário canônico definido em [`dominios.md`](../dominios.md).

## Para que serve

Quando alguém tenta classificar um critério com um domínio que não existe no catálogo, a skill `especificar` **recusa e oferece a lista canônica** — é a recusa que preserva a precisão no momento da spec. Mas recusar sem registrar joga fora o dado mais valioso que o método produz: a evidência de onde o vocabulário aperta.

Cada recusa vira uma linha aqui. O padrão acumulado é o que promove — ou não — um domínio novo ao catálogo.

## Como se lê

O critério de promoção **não é um número fixado a priori**, e isso é deliberado: qualquer número escolhido antes de existir evidência seria arbitrário. O log é o instrumento que revela o padrão — repetição do mesmo conceito sob nomes diferentes, ou insistência do mesmo nome em contextos distintos, é sinal mais confiável que uma contagem inventada.

Promoção também não é a única saída. Uma pressão recorrente pode revelar que o conceito já cabia num domínio existente e o problema era de documentação, não de catálogo.

## Registros

| data | spec | nome tentado | o que se queria expressar | domínio oferecido em substituição |
|---|---|---|---|---|

*(sem registros até o momento)*

## Formato da linha

- **data** — quando a recusa aconteceu, em `AAAA-MM-DD`
- **spec** — qual especificação estava sendo escrita
- **nome tentado** — exatamente como foi proposto, sem normalizar
- **o que se queria expressar** — o conceito por trás do nome, em uma frase; é este campo que revela o padrão, não o nome
- **domínio oferecido em substituição** — o que a skill sugeriu do catálogo, e se foi aceito
