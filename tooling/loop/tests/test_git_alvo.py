"""Guardas e histórico do alvo — spec: docs/specs/roteador-driver-invocacao.md."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import git_alvo


def _git(repo: Path, *args: str) -> str:
    concluido = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return concluido.stdout.strip()


def _repo(raiz: Path, branch: str) -> Path:
    repo = raiz / f"alvo-{branch}"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", branch)
    _git(repo, "config", "user.email", "loop@teste")
    _git(repo, "config", "user.name", "loop")
    (repo / "README.md").write_text("inicial\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "inicial")
    return repo


@pytest.fixture
def alvo(tmp_path: Path) -> Path:
    return _repo(tmp_path, "trabalho")


def test_working_tree_sujo_impede_comecar(alvo: Path):
    # spec:I5
    (alvo / "solto.py").write_text("x = 1\n", encoding="utf-8")
    (alvo / "README.md").write_text("mexido\n", encoding="utf-8")

    impedimentos = git_alvo.impedimentos(alvo)

    assert impedimentos
    juntos = " ".join(impedimentos)
    assert "solto.py" in juntos and "README.md" in juntos


def test_working_tree_limpo_nao_impede(alvo: Path):
    # spec:I5
    assert git_alvo.impedimentos(alvo) == ()


@pytest.mark.parametrize("branch", ["main", "master"])
def test_branch_default_impede_comecar(tmp_path: Path, branch: str):
    # spec:I6
    repo = _repo(tmp_path, branch)
    impedimentos = git_alvo.impedimentos(repo)
    assert impedimentos
    assert any(branch in impedimento for impedimento in impedimentos)


def test_branch_default_vem_do_remoto_quando_ele_existe(tmp_path: Path):
    # spec:I6 — com origin/HEAD configurado, o nome convencional não decide.
    repo = _repo(tmp_path, "entrega")
    _git(repo, "remote", "add", "origin", str(repo))
    _git(repo, "update-ref", "refs/remotes/origin/entrega", "HEAD")
    _git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/entrega")

    assert git_alvo.branch_default(repo) == "entrega"
    assert any("entrega" in i for i in git_alvo.impedimentos(repo))


def test_commit_de_tentativa_usa_assunto_e_trailer(alvo: Path):
    # spec:I7
    (alvo / "novo.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    sha = git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=2)

    assert sha
    assunto = _git(alvo, "log", "-1", "--format=%s")
    corpo = _git(alvo, "log", "-1", "--format=%b")
    assert assunto == "loop(alfa): codificar tentativa 2"
    assert "SLE-Loop: alfa#2" in corpo
    assert git_alvo.impedimentos(alvo) == ()


def test_commit_de_tentativa_recolhe_tudo_num_commit_so(alvo: Path):
    # spec:I7
    (alvo / "a.py").write_text("a\n", encoding="utf-8")
    (alvo / "b.py").write_text("b\n", encoding="utf-8")
    antes = _git(alvo, "rev-list", "--count", "HEAD")

    git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=1)

    assert int(_git(alvo, "rev-list", "--count", "HEAD")) == int(antes) + 1
    arquivos = _git(alvo, "show", "--name-only", "--format=", "HEAD").split()
    assert set(arquivos) == {"a.py", "b.py"}


def test_o_rebase_posterior_acha_os_commits_do_loop(alvo: Path):
    # spec:I7 — o trailer é contrato: é por ele que a limpeza os encontra.
    (alvo / "a.py").write_text("a\n", encoding="utf-8")
    git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=1)
    (alvo / "b.py").write_text("b\n", encoding="utf-8")
    git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=2)

    encontrados = _git(alvo, "log", "--grep=^SLE-Loop:", "--format=%s").splitlines()
    assert len(encontrados) == 2


def test_tentativa_sem_mudanca_nao_gera_commit_vazio(alvo: Path):
    # spec:I8
    antes = _git(alvo, "rev-list", "--count", "HEAD")

    sha = git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=1)

    assert sha is None
    assert _git(alvo, "rev-list", "--count", "HEAD") == antes


def test_modulo_nao_reescreve_historico_nem_publica():
    # spec:I9 — estrutural: a garantia é não existir o verbo no código.
    fonte = Path(git_alvo.__file__).read_text(encoding="utf-8")
    for proibido in ("push", "--amend", "rebase", "filter-branch", "reset --hard",
                     "--force", "cherry-pick", "commit-tree"):
        assert proibido not in fonte, f"git_alvo.py não pode conter {proibido!r}"


def test_head_devolve_o_sha_atual(alvo: Path):
    # spec:I10
    assert git_alvo.head(alvo) == _git(alvo, "rev-parse", "HEAD")


def test_head_muda_depois_do_commit_e_o_anterior_serve_de_base(alvo: Path):
    # spec:I10 — o ref base é o HEAD de antes da primeira tentativa.
    base = git_alvo.head(alvo)
    (alvo / "a.py").write_text("a\n", encoding="utf-8")
    git_alvo.commitar_tentativa(alvo, spec="alfa", tentativa=1)

    assert git_alvo.head(alvo) != base
    mudados = _git(alvo, "diff", "--name-only", f"{base}..HEAD").split()
    assert mudados == ["a.py"]
