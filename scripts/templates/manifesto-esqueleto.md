# Manifesto SLE — <preencher: nome do repositório>

> Formato e regras em [`dominios.md`](../dominios.md) (do repositório `echo-skills`). Este arquivo é a **declaração real** deste repositório.
>
> Gerado pelo instalador do SLE em <preencher: data>. Revise cada seção antes de considerar o repositório operacional.

## Domínios ativos

<preencher: lista dos domínios do catálogo canônico que efetivamente existem neste repositório. Se você não sabe, comece vazio — não invente domínios para "parecer completo">

## Domínios inativos

| domínio | por quê |
| --- | --- |
| <preencher> | <preencher: motivo — ex.: "não há autenticação neste repositório" > |

## Paths de produção

<preencher: padrões regex ancorados no início. Estes padrões dizem aos hooks e ao CI o que é código de produção. Sem esta seção, os defaults são usados: src/, lib/, app/, internal/, pkg/, cmd/>

- `<preencher: ex.: ^backend/app/>`
- `<preencher: ex.: ^frontend/src/>`

## Padrão de código local

<preencher: referência ao STYLE.md, .editorconfig, linter config, ou convenções específicas do repositório. Ausência degrada, não bloqueia — o Executor assume boas práticas gerais e sinaliza uma vez>

## Nível de rigor esperado

<preencher: um de "protótipo" / "produção padrão" / "produção crítica". Reflete a consequência real de bug em produção — não a auto-imagem do projeto>

## `tdd-aplicavel`

<preencher: um de "ortodoxo" (default, tudo é teste automatizado) / "parcial" (o que dá, automatiza; resto é plano manual) / "manual" (codebase legada onde TDD é inviável). Reflita honestamente o que a codebase suporta hoje — não o que você gostaria que ela suportasse>

## Hooks ativos

<preencher: lista dos hooks copiados pelo instalador em `tooling/hooks/`. Se você não habilitou hooks in-session no harness ainda, deixe claro que estão presentes mas não invocados>

## CI templates ativos

<preencher: lista dos workflows em `.github/workflows/`. O instalador os copiou em modo warning (`continue-on-error: true`). Remova o warning quando estiver pronto para bloqueio real, após 1-2 sprints ajustando falsos-positivos>

## Donos

<preencher: nomes ou grupos responsáveis pelas decisões arquiteturais de cada domínio. Em uso solo, escreva "não se aplica">

## Quando este manifesto muda

<preencher: liste os eventos que justificam revisão — ex.: entrada de nova disciplina, ativação de CI bloqueante, mudança de tdd-aplicavel>

## Histórico

- **<preencher: data>**: manifesto criado pelo instalador SLE. <preencher: motivo — ex.: "adoção inicial do método">
