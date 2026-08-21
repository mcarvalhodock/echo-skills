"""Testes da demanda versao-limpa-das-skills.

Cada teste cita, em comentário, o critério da spec que ele cobre
(`# spec:C1` etc.), como manda a convenção do repositório.

Estratégia de leitura: para os critérios ligados a YAML, extrai-se o bloco
entre `---` do arquivo, e o parser estrito (`yaml.safe_load`) decide se
carrega. Descrição com `: ` no meio é o defeito histórico que a spec vem
fechar; um parser lenient esconderia isso.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = REPO_ROOT / "docs" / "specs" / "versao-limpa-das-skills.md"
README_PATH = REPO_ROOT / "README.md"

SKILL_NAMES = (
    "especificar",
    "codificar",
    "verificar",
    "homologar",
    "orquestrar",
    "prototipar-frontend",
)

SKILLS_ANTES_QUEBRADAS = ("especificar", "codificar", "prototipar-frontend")

AGENT_FILES = ("sle-codificar.md", "sle-verificar.md", "sle-homologar.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end].strip("\n")


def _skill_frontmatter(skill_name: str) -> str:
    text = _read(REPO_ROOT / skill_name / "SKILL.md")
    fm = _extract_frontmatter(text)
    assert fm is not None, f"{skill_name}: frontmatter YAML ausente"
    return fm


def _agent_frontmatter(agent_file: str) -> str:
    text = _read(REPO_ROOT / ".claude" / "agents" / agent_file)
    fm = _extract_frontmatter(text)
    assert fm is not None, f"{agent_file}: frontmatter YAML ausente"
    return fm


class TestC1DecisaoDoGateNoTextoDaSpec:
    """A decisão aprovada no gate está registrada no texto da spec."""

    def test_spec_registra_formato_generico_unico_para_qualquer_harness(self) -> None:
        # spec:C1
        text = _read(SPEC_PATH)
        assert "formato genérico único" in text
        assert "harness" in text

    def test_spec_preserva_explicitamente_os_principios_atuais_do_metodo(self) -> None:
        # spec:C1
        text = _read(SPEC_PATH)
        # A decisão do gate exige preservação explícita — não basta reformar.
        assert "princípios" in text
        assert "invariantes" in text or "fases" in text or "gates" in text


class TestC2FrontmatterYAMLValida:
    """As seis skills carregam num parser YAML estrito."""

    @pytest.mark.parametrize("skill", SKILL_NAMES)
    def test_frontmatter_carrega_em_parser_yaml_estrito(self, skill: str) -> None:
        # spec:C2
        fm = _skill_frontmatter(skill)
        data = yaml.safe_load(fm)
        assert isinstance(data, dict), (
            f"{skill}: frontmatter não carregou como mapping"
        )
        assert data.get("name") == skill
        assert isinstance(data.get("description"), str)
        assert data["description"].strip()


class TestC3CarregamNoMesmoMecanismo:
    """As três antes quebradas passam a carregar pelo mesmo mecanismo das demais."""

    @pytest.mark.parametrize("skill", SKILLS_ANTES_QUEBRADAS)
    def test_skill_antes_quebrada_agora_carrega(self, skill: str) -> None:
        # spec:C3
        data = yaml.safe_load(_skill_frontmatter(skill))
        assert isinstance(data, dict)
        assert data.get("name") == skill

    def test_todas_as_seis_compartilham_o_mesmo_conjunto_de_chaves(self) -> None:
        # spec:C3
        # "Mesmo mecanismo" cai no molde comum: se uma tem chave a mais que
        # outra, o carregador precisa ramificar por skill, e o mecanismo
        # deixa de ser um só.
        shapes = {
            skill: frozenset(yaml.safe_load(_skill_frontmatter(skill)).keys())
            for skill in SKILL_NAMES
        }
        distintos = set(shapes.values())
        assert len(distintos) == 1, f"chaves divergentes entre skills: {shapes}"


class TestC4DisableModelInvocationRemovido:
    """O campo `disable-model-invocation: false` deixa de existir nas seis skills."""

    @pytest.mark.parametrize("skill", SKILL_NAMES)
    def test_campo_ausente_no_frontmatter(self, skill: str) -> None:
        # spec:C4
        data = yaml.safe_load(_skill_frontmatter(skill))
        assert "disable-model-invocation" not in data

    @pytest.mark.parametrize("skill", SKILL_NAMES)
    def test_campo_nao_aparece_no_texto_da_skill(self, skill: str) -> None:
        # spec:C4 — nem no corpo, para evitar reintrodução silenciosa por
        # copy-paste. A checagem no frontmatter cobre o carregamento;
        # esta cobre a fonte.
        text = _read(REPO_ROOT / skill / "SKILL.md")
        assert "disable-model-invocation" not in text


class TestC5AgentesSeguemFormatoGenerico:
    """`.claude/agents/*.md` segue o formato genérico único, sem `tools:` ou outra chave."""

    @pytest.mark.parametrize("agent_file", AGENT_FILES)
    def test_frontmatter_carrega_em_parser_yaml_estrito(self, agent_file: str) -> None:
        # spec:C5
        fm = _agent_frontmatter(agent_file)
        data = yaml.safe_load(fm)
        assert isinstance(data, dict)
        assert isinstance(data.get("name"), str) and data["name"].strip()
        assert isinstance(data.get("description"), str) and data["description"].strip()

    @pytest.mark.parametrize("agent_file", AGENT_FILES)
    def test_frontmatter_so_tem_name_e_description(self, agent_file: str) -> None:
        # spec:C5
        # "Sem especializações por harness": `tools:` é Claude-specific e é o
        # exemplo canônico dessa especialização; qualquer outra chave também
        # falha essa condição.
        data = yaml.safe_load(_agent_frontmatter(agent_file))
        assert set(data.keys()) == {"name", "description"}


class TestC6FonteVersionadaSuficiente:
    """O repo deixa de depender de cópia em `~/.claude/skills/`; a fonte versionada basta."""

    def test_readme_declara_que_a_fonte_versionada_e_suficiente(self) -> None:
        # spec:C6
        text = _read(README_PATH)
        assert "fonte versionada" in text.lower()

    def test_readme_diz_que_nao_depende_da_copia_antiga(self) -> None:
        # spec:C6
        text = _read(README_PATH).lower()
        # Uma afirmação explícita, para não ser satisfeita por sombra:
        # o texto precisa nomear a dependência que sai.
        assert "~/.claude/skills/" in text
        assert (
            "não depende" in text
            or "sem depender" in text
            or "deixa de depender" in text
        )


class TestC7DocumentacaoDeValidacaoDeCarga:
    """A documentação registra como validar a carga das seis skills."""

    def test_readme_tem_secao_de_validacao_de_carga(self) -> None:
        # spec:C7
        text = _read(README_PATH).lower()
        # Uma seção pesquisável — não uma menção lateral.
        assert "validação de carga" in text or "validar a carga" in text

    def test_documentacao_nomeia_o_harness_da_decisao_do_gate(self) -> None:
        # spec:C7
        # O procedimento tem que dizer *onde* se valida — Cursor é o harness
        # nomeado na justificativa da spec (as três que falhavam falhavam
        # nele). Sem harness nomeado, "como validar" é abstrato.
        text = _read(README_PATH).lower()
        assert "cursor" in text


class TestC8PreRequisitoDoPluginCursorAtendido:
    """O pré-requisito 'as seis skills carregam' fica atendido por esta spec."""

    @pytest.mark.parametrize("skill", SKILL_NAMES)
    def test_cada_uma_das_seis_carrega_em_parser_estrito(self, skill: str) -> None:
        # spec:C8
        # C8 é a mesma medida física de C2, olhada do ângulo do consumidor:
        # o `plugin-cursor` só destrava se as seis carregam. Testar as duas
        # separadamente deixa o vínculo explícito para quem lê o veredito.
        fm = _skill_frontmatter(skill)
        data = yaml.safe_load(fm)
        assert isinstance(data, dict)
        assert data.get("name") == skill
