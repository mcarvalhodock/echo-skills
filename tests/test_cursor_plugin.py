"""Testes da demanda `plugin-cursor` (`docs/specs/plugin-cursor.md`).

O que se mede aqui é o estado deste repositório, não um script portável — daí
viver na raiz e não em `tooling/ci/tests/`, que os repositórios consumidores
copiam junto com os workflows.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

# Pinado pela spec. A identidade se mede contra este ref, e não contra `HEAD`,
# que se move a cada commit da própria demanda.
REF_BASE = "1396c4f45aa89d96962d4ab0c67707dee76cb0a0"

PLUGIN_MANIFEST = REPO_ROOT / ".cursor-plugin" / "plugin.json"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
README = REPO_ROOT / "README.md"

KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DIRETORIOS_FORA_DA_VARREDURA = {".git", "__pycache__", ".pytest_cache"}


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _rodar_pytest(*alvos: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            *alvos,
            "-q",
            "--no-header",
            "--tb=no",
            "-rEf",
            "-p",
            "no:cacheprovider",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _manifesto_do_plugin() -> dict[str, Any]:
    return json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))


def _como_lista(valor: Any) -> list[str]:
    return [valor] if isinstance(valor, str) else list(valor)


def _skill_mds() -> list[Path]:
    return sorted(
        caminho
        for caminho in REPO_ROOT.rglob("SKILL.md")
        if not DIRETORIOS_FORA_DA_VARREDURA.intersection(
            caminho.relative_to(REPO_ROOT).parts
        )
    )


def _arquivos_de_agente() -> list[Path]:
    return sorted(AGENTS_DIR.iterdir())


def _relativo(caminho: Path) -> str:
    return caminho.relative_to(REPO_ROOT).as_posix()


def _secao(titulo: str) -> str:
    conteudo = README.read_text(encoding="utf-8")
    achado = re.search(
        rf"^##\s+{re.escape(titulo)}\s*$(.*?)(?=^##\s|\Z)",
        conteudo,
        re.DOTALL | re.MULTILINE,
    )
    assert achado is not None, f"README.md não tem a seção '{titulo}'"
    return achado.group(1)


class TestManifestoDoPlugin:
    def test_declara_nome_kebab_case_e_versao(self) -> None:
        # spec:M1
        assert PLUGIN_MANIFEST.is_file()
        manifesto = _manifesto_do_plugin()
        assert KEBAB_CASE.match(manifesto["name"]), manifesto["name"]
        assert manifesto["version"]

    def test_skills_aponta_para_as_seis_pastas_da_raiz(self) -> None:
        # spec:M2
        declarados = _como_lista(_manifesto_do_plugin()["skills"])
        assert len(declarados) == 6
        for caminho in declarados:
            assert caminho.startswith("./"), caminho
            assert ".." not in Path(caminho).parts, caminho
        # O plugin tem a raiz do repositório como raiz: é lá que mora
        # `.cursor-plugin/`.
        assert {(REPO_ROOT / c).resolve() for c in declarados} == {
            skill_md.parent.resolve() for skill_md in _skill_mds()
        }

    def test_agents_aponta_para_claude_agents(self) -> None:
        # spec:M3
        declarados = _como_lista(_manifesto_do_plugin()["agents"])
        for caminho in declarados:
            assert caminho.startswith("./"), caminho
            assert ".." not in Path(caminho).parts, caminho
        assert {(REPO_ROOT / c).resolve() for c in declarados} == {
            AGENTS_DIR.resolve()
        }


class TestLayoutIntacto:
    def test_nenhuma_pasta_de_skill_mudou_de_lugar(self) -> None:
        # spec:M4
        diff = _git("diff", "--name-status", REF_BASE)
        assert diff.returncode == 0, diff.stderr
        renomeados = [
            linha for linha in diff.stdout.splitlines() if linha.startswith("R")
        ]
        assert renomeados == []

    def test_as_tres_definicoes_de_agente_seguem_nos_mesmos_caminhos(self) -> None:
        # spec:M5
        no_ref_base = _git("ls-tree", "-r", "--name-only", REF_BASE, ".claude/agents/")
        assert no_ref_base.returncode == 0, no_ref_base.stderr
        esperados = sorted(
            linha.strip() for linha in no_ref_base.stdout.splitlines() if linha.strip()
        )
        assert len(esperados) == 3
        assert [_relativo(p) for p in _arquivos_de_agente()] == esperados

    def test_um_unico_skill_md_por_skill(self) -> None:
        # spec:M6
        skill_mds = _skill_mds()
        assert len(skill_mds) == 6
        assert len({skill_md.parent for skill_md in skill_mds}) == 6
        pacote = PLUGIN_MANIFEST.parent
        assert [s for s in skill_mds if pacote in s.parents] == []

    def test_skills_e_agentes_identicos_ao_ref_base(self) -> None:
        # spec:M7
        alvos = [_relativo(p) for p in _skill_mds() + _arquivos_de_agente()]
        diff = _git("diff", "--exit-code", REF_BASE, "--", *alvos)
        assert diff.returncode == 0, diff.stdout

    def test_instaladores_identicos_ao_ref_base(self) -> None:
        # spec:M8
        diff = _git(
            "diff",
            "--exit-code",
            REF_BASE,
            "--",
            "scripts/install.ps1",
            "scripts/install.sh",
        )
        assert diff.returncode == 0, diff.stdout


class TestSuitesQueNaoPodemRegredir:
    def test_scripts_tests_nao_ganha_reprovacao_nova(self) -> None:
        # spec:M9
        execucao = _rodar_pytest("scripts/tests")
        vermelhos = [
            linha.split()[1]
            for linha in execucao.stdout.splitlines()
            if linha.startswith(("FAILED ", "ERROR "))
        ]
        # Subconjunto, e não igualdade: no ref base reprovam os 14 de
        # `test_install_sh.py`, por defeito de ambiente que a spec põe fora de
        # escopo — e quando ele for consertado, este teste segue verde.
        assert [
            v for v in vermelhos if not v.startswith("scripts/tests/test_install_sh.py::")
        ] == []

    def test_os_quatorze_testes_de_tooling_ci_passam(self) -> None:
        # spec:M13
        execucao = _rodar_pytest("tooling/ci/tests")
        assert execucao.returncode == 0, execucao.stdout
        contagem = re.search(r"(\d+) passed", execucao.stdout)
        assert contagem is not None, execucao.stdout
        assert int(contagem.group(1)) >= 14


class TestReadme:
    def test_arvore_do_repositorio_nomeia_o_pacote(self) -> None:
        # spec:M11
        assert ".cursor-plugin/" in _secao("O que tem neste repo")

    def test_instalacao_poe_o_plugin_ao_lado_do_instalador(self) -> None:
        # spec:M12
        instalacao = _secao("Instalação")
        assert "install.sh" in instalacao
        assert "install.ps1" in instalacao
        assert ".cursor-plugin" in instalacao
        assert "ao lado" in instalacao
