# Hook: block-validator-writing-code

Enforça a **segunda invariante do SLE**: Executor ≠ Validator.

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
