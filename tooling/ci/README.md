# SLE — CI enforcement

Três verificadores independentes que fecham o loop de disciplina do SLE no nível do pipeline. Cada verificador é um script Python autocontido (`tooling/ci/scripts/`) invocado por um workflow GitHub Actions (`tooling/ci/*.yml`). O script é portável — GitLab CI, CircleCI, Jenkins, ou pre-push local funcionam mudando apenas o wrapper.

## Componentes

### 1. `spec_test_parity.py` + `spec-test-parity.yml`

**Pergunta:** cada spec declara seus testes? Cada teste declarado existe?

**Convenção:** a spec (arquivo em `docs/specs/`) declara uma seção `## Testes vinculados` com uma bullet list de caminhos:

```markdown
## Testes vinculados

- `tests/test_feature.py`
- `tests/test_feature_edge_cases.py`
```

O script falha se:

- Um caminho declarado não existe no filesystem
- Uma spec produtiva (excluindo `*-log.md`, `*-fidelidade.md`, `*-manual-validation.md`) não declara testes E não tem `tdd: parcial` ou `tdd: manual` no cabeçalho (v3 do método)

### 2. `criterion_coverage.py` + `criterion-coverage.yml`

**Pergunta:** cada critério de aceite (`A1`, `A2`, `C1`, ...) aparece em pelo menos um teste?

**Convenção:** critérios são declarados na spec como `- **A1**: descrição`. Testes marcam cobertura com o texto `spec:A1` (case-insensitive, em qualquer lugar do arquivo — comentário, nome de teste, tag):

```python
def test_criterio_a1_valida_input():
    # spec:A1
    ...
```

Ou para itens não-automatizáveis (v3: TDD parcial/manual), a marca aparece em `<spec>-manual-validation.md`:

```markdown
- **spec:A1** — verificado manualmente na tela X clicando em Y.
```

### 3. `pr_spec_diff.py` + `pr-spec-diff.yml`

**Pergunta:** alteração em código de produção veio acompanhada de alteração em spec?

Falha o PR se algum arquivo em paths de produção (declarados em `.sle/manifesto.md` ou defaults: `src/`, `lib/`, `app/`, `internal/`, `pkg/`, `cmd/`) foi tocado sem que nenhum arquivo em `docs/specs/` (excluindo logs e testes de fidelidade) tenha sido alterado no mesmo PR.

## Ativação em outros CIs

Os scripts são invocáveis diretamente — mudam apenas os wrappers.

### GitLab CI

```yaml
sle-spec-test-parity:
  image: python:3.11
  script:
    - python tooling/ci/scripts/spec_test_parity.py
```

### CircleCI

```yaml
jobs:
  sle-criterion-coverage:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run: python tooling/ci/scripts/criterion_coverage.py
```

### Pre-push hook local

```bash
#!/usr/bin/env bash
python tooling/ci/scripts/spec_test_parity.py || exit 1
python tooling/ci/scripts/criterion_coverage.py || exit 1
```

## Testes

```powershell
pytest tooling/ci/tests/ -v
```

16 testes cobrem: extração de critérios, cobertura completa/parcial, classificação de paths, três cenários de PR diff, ignorar sufixos de logs.

## Limitações conhecidas

1. **Convenções textuais.** Todo enforcement depende do consumidor seguir as convenções (seção `Testes vinculados`, marcador `spec:AX`, sufixos `-log.md`/`-fidelidade.md`). Repositório que ignora as convenções pode passar os checkers sem estar em conformidade real.
2. **`pr_spec_diff` depende de `git diff` funcional.** Requer histórico do base ref no ambiente CI (`fetch-depth: 0` no checkout).
3. **`criterion_coverage` não verifica se o teste realmente valida o critério.** Só que o marcador existe. Isso é uma decisão consciente — verificação profunda é papel humano na homologação.
4. **Falso-positivos são preferíveis a falso-negativos.** O CI é um sinal de disciplina, não um substituto do Validator.
