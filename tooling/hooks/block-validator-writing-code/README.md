# Hook: block-validator-writing-code

> **SUPERSEDIDO NA v5 DO MÉTODO — não habilite sem ler isto.**
>
> Este hook enforça a redação antiga da invariante 2, *"o Validator não escreve código de
> produção"*. A v5 trocou o eixo dessa invariante para **"ninguém assina o que escreveu"**:
> escrever passou a ser permitido em emenda dirigida pelo humano, e o que se protege é a
> **atestação**, não a escrita. Ver `metodologia-sle.md` (As 4 invariantes) e a seção
> "Emenda" em `validator/SKILL.md`.
>
> Consequência prática: **em repositório na v5, este hook bloqueia comportamento que o
> método agora permite** — o Validador tentando aplicar uma emenda que o humano pediu vai
> bater na parede.
>
> Ele não foi removido porque a regra que enforça continua correta **durante a Fase
> Traduzir**: antes de existir código, o Validador implementar por conta própria destrói a
> suíte que ele deveria estar derivando da spec. O que falta é o hook distinguir fase de
> emenda, e ele não distingue — não recebe nem uma coisa nem outra como entrada.
>
> **Decisão pendente do humano**, e nenhuma saída é obviamente certa: ensinar o hook a
> receber `--fase` e `--emenda`; restringi-lo à Fase Traduzir; ou aposentá-lo e deixar a
> invariante 2 viver só no registro de atestação. Enquanto não se decidir, o hook fica como
> está e **não deve ser habilitado em repositório que opere na v5**.

Enforça a **redação v4 da segunda invariante do SLE**: Executor ≠ Validator.

## O que faz

Bloqueia operações de escrita/edição/deleção quando a skill ativa é `validator` e o caminho alvo bate com padrões de código de produção declarados no manifesto (ou padrões default).

Permite:

- Escrita em `tests/`, `test/`, `spec/`, `__tests__/` — testes automatizados (BDD, contrato arquitetural, fidelidade)
- Escrita em `docs/specs/*-log.md` — homologation log
- Escrita em `docs/specs/*-manual-validation.md` — plano de validação manual (v3: TDD parcial/manual)
- Escrita em `docs/specs/*-fidelidade.md` — testes de fidelidade (v2: N3)
- Escrita em `.sle/pressao-metodo.md` — pressão método
- Escrita em `.sle/pressao-catalogo.md` e `.echo/pressao-catalogo.md` — pressão catálogo (legado)

## Invocação direta

```powershell
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path src/app.ts `
  --action edit

# Exit code 1: BLOQUEADO
```

```powershell
python tooling/hooks/block-validator-writing-code/hook.py `
  --role validator `
  --path tests/app.test.ts `
  --action write

# Exit code 0: permitido
```

## Configuração no manifesto

Idem hook `block-designer-writing-code` — seção `Paths de produção` no `.sle/manifesto.md`.

## Ativação no harness

Idem hook `block-designer-writing-code` — registrar como `PreToolUse` (Claude Code) ou `beforeFileWrite` (Cursor) com a mesma estrutura. Fallback via pre-commit hook do git funciona igual.

## Testes

```powershell
pytest tooling/hooks/tests/test_block_validator.py -v
```

## Limitações conhecidas

1. **Detecção de identidade da skill ativa depende do harness.** Idem hook 1.
2. **Testes com nomes fora do convencional podem ser bloqueados.** Padrões default: `tests/`, `test/`, `spec/`, `__tests__/`. Repositórios com pasta de testes atípica precisam ajustar o hook (por enquanto, editar `ALLOWED_VALIDATOR_PATH_PATTERNS`; futuramente, ler do manifesto).
3. **Não distingue código embutido em arquivos permitidos.** Um `test.ts` que na prática exporta produção não é detectado — revisão humana continua responsável.
