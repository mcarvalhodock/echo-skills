# instalador-alvo-e-remocao-do-loop

## Intenção
Quem roda `install.sh` contra um repositório que ainda não existe no disco recebe o mesmo resultado que o `install.ps1` já dá; e o repositório deixa de carregar `tooling/loop`, que não é mais usado.

## Depende de
Nenhuma.

## Critérios

- [ ] **A1** `plataforma` — `install.sh --components ci --target-repo <caminho inexistente>` cria o diretório-alvo.
- [ ] **A2** `plataforma` — O mesmo comando sai com código 0.
- [ ] **A3** `plataforma` — `scripts/tests/_helpers.py` deixa de anular `BASH_BIN` em `win32`.
- [ ] **A4** `plataforma` — Com `bash` no PATH, nenhum teste de `scripts/tests/test_install_sh.py` é pulado.
- [ ] **A5** `plataforma` — Todos os testes de `test_install_sh.py` passam.
- [ ] **A6** `plataforma` — Existe teste, por instalador, que roda contra diretório-alvo inexistente.
- [ ] **A7** `plataforma` — Dado um `python3` no PATH que não reporta versão e um `python` 3.11+ funcional, `install.sh` instala o componente `ci`.
- [ ] **A8** `plataforma` — A resolução de `bash` em `scripts/tests/_helpers.py` rejeita candidato que não executa e segue para o próximo.
- [ ] **B1** `plataforma` — `tooling/loop/` não existe no repositório.
- [ ] **B2** `plataforma` — `scripts/sle` e `scripts/sle.ps1` não existem no repositório.
- [ ] **B3** `plataforma` — `README.md` não cita `tooling/loop` nem os comandos `sle`.
- [ ] **B4** `plataforma` — Em `.sle/manifesto.md`, as seções "Ferramental disponível" e a descrição do componente deixam de descrever o loop.
- [ ] **B5** `plataforma` — O registro histórico fica byte-idêntico: `docs/specs/loop-*.md`, `docs/specs/roteador-*.md`, `docs/specs/sle-*.md`, `docs/prototipos/velha-residuo.md` e a seção "Histórico" de `.sle/manifesto.md`.
- [ ] **B6** `plataforma` — Nenhum arquivo versionado fora desse registro histórico referencia `tooling/loop` ou `scripts/sle`.
- [ ] **B7** `plataforma` — `tooling/ci/` permanece, e seus 14 testes passam.

## Contrato técnico

A remoção é `git rm`: o histórico do git preserva o código, e é isso que torna a deleção segura sem manter arquivo órfão na árvore.

**Registro histórico não se reescreve.** As specs e vereditos de `loop-*`, `roteador-*` e `sle-*` documentam por que o loop foi construído, o que foi medido nele e por que foi recusado — apagá-los removeria o argumento contra reconstruí-lo. Pela mesma razão, as entradas datadas da seção "Histórico" do manifesto e a ancoragem de `velha-residuo.md` (que cita `tooling/loop/painel.py`) ficam intactas: são o que o repositório registrou na época, não descrição do estado atual. **B5** é o guarda disso, e é o critério que impede a limpeza de virar reescrita.

Os instaladores **não** referenciam `tooling/loop` nem `scripts/sle` — `.sle/manifesto.md:78` registra que não copiar o loop para o consumidor é deliberado. Por isso a Fatia B não toca `scripts/install.*`, e as duas fatias não colidem.

A suíte de `tooling/` cai de 313 para 14 testes. Isso é a remoção, não regressão: 299 pertenciam a `tooling/loop`.

**A3** existe porque o opt-out atual mente sobre a causa: `_helpers.py:31-32` encontra o bash e o descarta em `win32` exibindo "bash não disponível". Foi ele que manteve A1 invisível por pelo menos um ciclo — o defeito é de plataforma, não do Windows, e falharia igual num runner Linux.

**A7 e A8 são a mesma regra, aplicada nos dois lados: estar no PATH não é executar.** Ambos foram descobertos ao implementar, e entram como critério porque **A5** não fecha sem eles:

- `command -v python3` acerta o atalho da Microsoft Store, que está no PATH, não roda e imprime instrução de instalação em vez de versão. Parar no primeiro candidato desabilitava o `ci` com um Python 3.12 ao lado — e `test_workflows_recebem_warning_mode` exige o `ci` instalado.
- Removido o descarte de `win32`, `shutil.which("bash")` resolve para o bash do WSL, que falha com `execvpe /bin/bash failed`. Era isso que o opt-out escondia atrás de "bash não disponível".

Em ambos, o candidato é **sondado**, não presumido: quem não responde é descartado e a busca segue.

## Fora de escopo

- **Reescrever ou apagar as specs históricas do loop.** Decisão do humano: o código sai, o registro fica.
- **Substituir o loop por outra automação.** Ele saiu porque encadear à mão bastou; repor automação agora é refazer o que foi recusado.
- **Mexer em `tooling/ci/`.** Componente independente, com dono e testes próprios — **B7** é o guarda de que ele não vá junto por arrasto.
- **Alterar `install.ps1`.** Ele já cria o alvo e já sai 0; a paridade que falta é do lado `sh`.

## Plano

1. **`scripts/install.sh`** — criar o diretório-alvo antes de escrever `SLE-SETUP.md` (`:591` é onde estoura hoje) (A1, A2); e sondar cada candidato a Python em vez de parar no primeiro do PATH (A7).
2. **`scripts/tests/_helpers.py`** — remover o descarte de `BASH_BIN` em `win32` e sondar o candidato a bash (A3, A4, A8).
3. **`scripts/tests/test_install_sh.py` e `test_install_ps1.py`** — teste de alvo inexistente por instalador (A5, A6).
4. **`git rm -r tooling/loop scripts/sle scripts/sle.ps1`** (B1, B2).
5. **`README.md` e `.sle/manifesto.md`** — retirar a árvore, a seção de comandos `sle` e a descrição do componente, sem tocar em "Histórico" (B3, B4, B5).
6. **Varredura** — `git grep` por `tooling/loop` e `scripts/sle` fora do registro histórico (B6, B7).

**Duas fatias, ambas `plataforma`, cada uma fecha sozinha; a ordem entre elas é indiferente:**

- **Fatia A** (A1–A8): o defeito do instalador. Passos 1–3.
- **Fatia B** (B1–B7): a remoção do loop. Passos 4–6.

Vem A primeiro por ser conserto em código que fica, enquanto B é subtrativa — se o apetite mudar no meio, o conserto já está dentro.

## Perguntas em aberto

Vazio.
