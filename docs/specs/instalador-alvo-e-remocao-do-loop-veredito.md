# instalador-alvo-e-remocao-do-loop — veredito

Base: `docs/specs/instalador-alvo-e-remocao-do-loop.md` contra `git diff e1c05f2..HEAD` limitado a `.`, mais o trabalho não commitado (`git status`: exclusões de `tooling/loop`, `scripts/sle*` em stage; `.sle/manifesto.md`, `README.md`, `scripts/install.sh`, `scripts/tests/_helpers.py`, `test_install_sh.py`, `test_install_ps1.py` modificados; `scripts/tests/test_resolucao_de_bash.py` novo, não rastreado). Suítes executadas.

- **A1** — atendido
- **A2** — atendido
- **A3** — atendido
- **A4** — atendido
- **A5** — atendido
- **A6** — atendido
- **A7** — atendido
- **A8** — atendido
- **B1** — atendido
- **B2** — atendido
- **B3** — atendido
- **B4** — atendido
- **B5** — atendido
- **B6** — atendido
- **B7** — atendido

## Por quê

**A1** — `scripts/install.sh:590` ganhou `mkdir -p "$ARG_TARGET_REPO"` dentro de `generate_setup_guide`, imediatamente antes do redirecionamento que estourava. `TestAlvoInexistente::test_cria_o_diretorio_alvo` asserta `not fake_target.exists()` antes e `fake_target.is_dir()` depois; passa.

**A2** — `test_sai_com_zero_em_alvo_inexistente` afirma `result.returncode == 0` sobre o mesmo comando (`--components ci --target-repo <inexistente>`); passa. A guarda é separada da de A1 de propósito: criar o diretório e sair 0 são falhas distintas, e o teste de A1 não lê o código de saída.

**A3** — o bloco `if BASH_BIN and sys.platform.startswith("win"): BASH_BIN = None` foi removido de `scripts/tests/_helpers.py`, junto com o `import sys` que só existia para ele. `BASH_BIN` agora vem de `_find_working_bash()`, que não consulta plataforma em lugar nenhum.

**A4** — `python -m pytest scripts/tests/test_install_sh.py -q -rs`: **13 passed**, nenhuma linha de skip no sumário. Nesta máquina `_helpers.BASH_BIN` resolve para `C:\Program Files\Git\usr\bin\bash.EXE` — o `run_sh` chega ao `pytest.skip` zero vezes.

**A5** — a mesma execução fecha em 13 passed, 0 failed. A suíte inteira de `scripts/tests` também fecha verde (31 passed), o que cobre os testes novos de `_helpers` e do lado ps1.

**A6** — dois testes, um por instalador, ambos contra alvo que ainda não existe: `test_install_sh.py::TestAlvoInexistente` (dois casos, A1 e A2) e `test_install_ps1.py::TestAlvoInexistente::test_cria_o_diretorio_alvo`, este último rotulado como paridade. O do ps1 é regressão pura — o comportamento já existia — e é o que impede a paridade recém-conquistada de se perder do outro lado.

**A7** — `test_python_available` virou laço `for py_bin in python3 python`, com `continue` em cada uma das três formas de o candidato não responder: não estar no PATH, o `--version` sair não-zero, e a saída não casar com `Python X.Y`. `TestDeteccaoDePython::test_ignora_python3_que_nao_reporta_versao` planta um stub `python3` no início do `PATH` (via o parâmetro novo `prefixo_de_path` de `run_sh`) que imprime instrução de instalação e sai 9009 — imitando o atalho da Store — e exige `returncode == 0` **e** `.github/workflows` criado no alvo. Isto é o critério na sua forma útil: o `ci` instalado apesar do candidato quebrado, não só o script não quebrando. Passa.

**A8** — `_find_working_bash()` sonda cada candidato com `[candidato, "-c", "echo sle-ok"]` e só aceita quem sai 0 **e** imprime o marcador; `OSError`/`SubprocessError` caem em `continue`, e a lista segue para os caminhos fixos do Git for Windows. `scripts/tests/test_resolucao_de_bash.py` cobre os dois lados por monkeypatch: `test_descarta_candidato_que_nao_executa` faz a sonda levantar `OSError("execvpe /bin/bash failed")` — o modo de falha exato do bash do WSL, que era o que o descarte de A3 escondia — e exige `None`; `test_aceita_candidato_que_responde` exige o caminho de volta. Ressalva declarada, que não muda o veredito: este arquivo está **não rastreado** (`git status`), então o critério está atendido na árvore de trabalho e ainda não no que o commit entregaria.

**B1** — `tooling/` contém apenas `ci/` e `hooks/`. Os 46 arquivos de `tooling/loop/` aparecem como `deleted` em stage, não como órfãos na árvore.

**B2** — `scripts/` contém `install.ps1`, `install.sh`, `templates/`, `tests/`. `scripts/sle` e `scripts/sle.ps1` estão como `deleted` em stage. Ambos saíram por `git rm`, como o contrato técnico exige: o histórico preserva o código.

**B3** — `git grep -E "tooling/loop|scripts/sle" -- README.md` não retorna nada. Saíram as duas linhas da árvore de arquivos, o bloco de comandos `sle` inteiro (`repo add`/`painel`/`pedir`/`rodar`), o parágrafo do console, o de códigos de saída e o "Sem API key e sem SDK", além dos dois links para `tooling/loop/README.md`. O texto que ficou no lugar registra que houve automação e que ela saiu, apontando para `docs/specs/loop-*.md` e `sle-*.md` — coerente com a decisão de manter o registro fora do README.

**B4** — em `.sle/manifesto.md`, "Ferramental disponível" perdeu o trecho "e o roteador do loop em `tooling/loop/`", ficando só o CI; e a seção `## Loop` inteira (13 linhas: núcleo puro, casca impura, ferramenta, specs, o parágrafo do "mora com o método" e o link do guia) foi removida. Nenhuma descrição do loop sobrou fora do "Histórico".

**B5** — `git diff e1c05f2 --stat -- docs/specs/loop-*.md docs/specs/roteador-*.md docs/specs/sle-*.md docs/prototipos/velha-residuo.md` retorna vazio: nenhum byte alterado em nenhum dos quatro conjuntos. Quanto ao "Histórico" de `.sle/manifesto.md`: as duas únicas hunks do diff do manifesto são `@@ -25,7` e `@@ -66,19`, e a seção `## Histórico` começa na linha 91 — nenhuma hunk a alcança. A entrada datada de 2026-08-12 que anuncia o nascimento de `tooling/loop/` continua lá, palavra por palavra.

**B6** — `git grep -lE "tooling/loop|scripts/sle" -- .` filtrado contra o registro histórico (`docs/specs/loop-*`, `roteador-*`, `sle-*`, `docs/prototipos/velha-residuo.md`, e a seção "Histórico" do manifesto) devolve **lista vazia**. A única ocorrência em arquivo que não é spec do loop é `.sle/manifesto.md:96`, e ela está dentro de "Histórico" — exatamente o que B5 manda preservar. Consistente também com o contrato: `scripts/install.ps1` e `scripts/install.sh` nunca referenciaram o loop, e a Fatia B de fato não os tocou (o diff de `install.sh` é só de Fatia A).

**B7** — `tooling/ci/` permanece na árvore e `python -m pytest tooling/ci -q` fecha em **14 passed**. Bate com o número declarado no contrato técnico, o que confirma que a queda de 313 para 14 é a subtração prevista e não arrasto sobre o `ci`.
