"""Testes do hook block-executor-writing-tests-semantically."""

from __future__ import annotations

from pathlib import Path

from conftest import executor_hook


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestSnapshotEComparacao:
    def test_snapshot_captura_nomes_de_testes_python(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "tests" / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n\n"
            "def test_multiplicacao():\n    assert 2 * 3 == 6\n",
        )
        snapshot = executor_hook.build_snapshot(tmp_path / "tests", tmp_path)
        assert len(snapshot.files) == 1
        sig = next(iter(snapshot.files.values()))
        assert sig.test_names == ("test_multiplicacao", "test_soma")
        assert sig.assertion_count == 2

    def test_snapshot_captura_nomes_de_testes_jest(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "tests" / "a.test.ts",
            "test('soma funciona', () => { expect(1+1).toBe(2); });\n"
            "it('multiplicacao funciona', () => { expect(2*3).toBe(6); });\n",
        )
        snapshot = executor_hook.build_snapshot(tmp_path / "tests", tmp_path)
        sig = next(iter(snapshot.files.values()))
        assert "soma funciona" in sig.test_names
        assert "multiplicacao funciona" in sig.test_names
        assert sig.assertion_count == 2

    def test_snapshot_captura_nomes_de_testes_go(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "tests" / "a_test.go",
            "package main\n\nfunc TestSoma(t *testing.T) {\n"
            "    if 1+1 != 2 { t.Errorf(\"falhou\") }\n"
            "}\n",
        )
        snapshot = executor_hook.build_snapshot(tmp_path / "tests", tmp_path)
        sig = next(iter(snapshot.files.values()))
        assert sig.test_names == ("TestSoma",)


class TestBloqueiaAlteracaoSemanticaQuandoRoleEExecutor:
    def test_executor_adicionando_teste_e_bloqueado(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n",
        )
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n\n"
            "def test_novo():\n    assert True\n",
        )
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert not divergence.is_empty()
        assert any("test_novo" in item for item in divergence.added_tests)

    def test_executor_removendo_teste_e_bloqueado(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n\n"
            "def test_multiplicacao():\n    assert 2 * 3 == 6\n",
        )
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n",
        )
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert not divergence.is_empty()
        assert any("test_multiplicacao" in item for item in divergence.removed_tests)

    def test_executor_alterando_assertion_e_bloqueado(
        self, tmp_path: Path
    ) -> None:
        tests_dir = tmp_path / "tests"
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n",
        )
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 3\n",
        )
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert not divergence.is_empty()
        assert divergence.changed_assertions

    def test_executor_criando_arquivo_de_teste_e_bloqueado(
        self, tmp_path: Path
    ) -> None:
        tests_dir = tmp_path / "tests"
        _write(tests_dir / "test_a.py", "def test_soma():\n    assert True\n")
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(tests_dir / "test_b.py", "def test_novo():\n    assert True\n")
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert "tests/test_b.py" in divergence.new_files


class TestNaoInterfereEmOperacoesPermitidas:
    def test_refactor_nao_semantico_preserva_assinatura(
        self, tmp_path: Path
    ) -> None:
        tests_dir = tmp_path / "tests"
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n"
            "    x = 1\n"
            "    y = 1\n"
            "    assert x + y == 2\n",
        )
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(
            tests_dir / "test_a.py",
            "def make_operands():\n"
            "    return 1, 1\n\n"
            "def test_soma():\n"
            "    x, y = make_operands()\n"
            "    assert x + y == 2\n",
        )
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert divergence.is_empty(), (
            f"refactor não-semântico não deveria disparar: {divergence.describe()}"
        )

    def test_reordenacao_de_testes_nao_dispara(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert 1 + 1 == 2\n\n"
            "def test_multiplicacao():\n    assert 2 * 3 == 6\n",
        )
        before = executor_hook.build_snapshot(tests_dir, tmp_path)

        _write(
            tests_dir / "test_a.py",
            "def test_multiplicacao():\n    assert 2 * 3 == 6\n\n"
            "def test_soma():\n    assert 1 + 1 == 2\n",
        )
        after = executor_hook.build_snapshot(tests_dir, tmp_path)

        divergence = executor_hook.compare_snapshots(before, after)
        assert divergence.is_empty()


class TestNaoAplicaAOutrasRoles:
    def test_validator_pode_alterar_semantica(self, tmp_path: Path) -> None:
        tests_dir = tmp_path / "tests"
        _write(tests_dir / "test_a.py", "def test_soma():\n    assert True\n")
        snapshot_file = tmp_path / "snap.json"
        snapshot_file.write_text(
            executor_hook.build_snapshot(tests_dir, tmp_path).to_json(),
            encoding="utf-8",
        )
        _write(
            tests_dir / "test_a.py",
            "def test_soma():\n    assert True\n\n"
            "def test_novo():\n    assert False\n",
        )

        import argparse

        args = argparse.Namespace(
            tests_dir=str(tests_dir),
            snapshot=str(snapshot_file),
            role="validator",
            project_root=str(tmp_path),
        )
        exit_code = executor_hook.cmd_check(args)
        assert exit_code == 0


class TestErrosDeInvocacao:
    def test_snapshot_faltando_retorna_3(self, tmp_path: Path) -> None:
        import argparse

        args = argparse.Namespace(
            tests_dir=str(tmp_path),
            snapshot=str(tmp_path / "inexistente.json"),
            role="executor",
            project_root=str(tmp_path),
        )
        exit_code = executor_hook.cmd_check(args)
        assert exit_code == 3
