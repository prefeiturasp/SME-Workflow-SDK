"""Fixtures compartilhadas para os testes."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from sme_workflow_sdk import ConfiguradorWorkflow
from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow
from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.resultado import ResultadoWorkflow

WORKFLOW_EXEMPLO = """\
estados:
  aberto:
    acoes:
      aprovar:
        proximo_estado: aprovado
        terminal: false
      rejeitar:
        proximo_estado: rejeitado
        terminal: true

  aprovado:
    acoes:
      iniciar_execucao:
        proximo_estado: em_execucao
        terminal: false

  em_execucao:
    acoes:
      finalizar:
        proximo_estado: concluido
        terminal: true

  rejeitado:
    acoes: null

  concluido:
    acoes: null
"""

VALORES_INVALIDOS_IDENTIFICADOR = [
    "_",
    "_privado",
    "abc_",
    "A_",
    "a__b",
    "__x",
    "a_1",
    "123abc",
    "abc1",
    "123",
    "abc-def",
    "abc def",
    "abc.def",
    "1.5",
    "-42",
    "execução",
    "ação",
]

VALORES_VALIDOS_IDENTIFICADOR = [
    "a",
    "A",
    "Acao",
    "em_execucao",
    "abc_def",
    "abc_def_ghi",
    "AbcDef",
]


@pytest.fixture
def yaml_valido(tmp_path: Path) -> Path:
    """Cria um arquivo YAML com um workflow de exemplo válido"""
    arquivo = tmp_path / "workflow.yaml"
    arquivo.write_text(WORKFLOW_EXEMPLO, encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_extensao_yml(tmp_path: Path) -> Path:
    """Cria um YAML válido com extensão .yml."""
    arquivo = tmp_path / "workflow.yml"
    arquivo.write_text(WORKFLOW_EXEMPLO, encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_vazio(tmp_path: Path) -> Path:
    """Cria um YAML vazio."""
    arquivo = tmp_path / "vazio.yaml"
    arquivo.write_text("", encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_apenas_comentarios(tmp_path: Path) -> Path:
    """Cria um YAML contendo apenas comentários."""
    arquivo = tmp_path / "comentarios.yaml"
    arquivo.write_text("# apenas um comentário\n# outro\n", encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_raiz_lista(tmp_path: Path) -> Path:
    """Cria um YAML cuja raiz é uma lista, não um dicionário."""
    arquivo = tmp_path / "lista.yaml"
    arquivo.write_text("- item1\n- item2\n", encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_raiz_escalar(tmp_path: Path) -> Path:
    """Cria um YAML cuja raiz é um escalar (string)."""
    arquivo = tmp_path / "escalar.yaml"
    arquivo.write_text("apenas uma string\n", encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_multiplos_documentos(tmp_path: Path) -> Path:
    """Cria um YAML com múltiplos documentos separados por '---'."""
    arquivo = tmp_path / "multi.yaml"
    arquivo.write_text(
        "nome: doc1\n---\nnome: doc2\n",
        encoding="utf-8",
    )
    return arquivo


@pytest.fixture
def yaml_sintaxe_invalida(tmp_path: Path) -> Path:
    """Cria um YAML com sintaxe inválida."""
    arquivo = tmp_path / "invalido.yaml"
    arquivo.write_text("nome: [sem fechamento\n", encoding="utf-8")
    return arquivo


@pytest.fixture
def yaml_encoding_invalido(tmp_path: Path) -> Path:
    """Cria um arquivo com bytes inválidos em UTF-8 (latin-1)."""
    arquivo = tmp_path / "latin1.yaml"
    arquivo.write_bytes(b"nome: \xe7\xe3o\n")  # latin-1: 'ção'
    return arquivo


@pytest.fixture
def arquivo_extensao_invalida(tmp_path: Path) -> Path:
    """Cria um arquivo .txt com conteúdo YAML válido."""
    arquivo = tmp_path / "workflow.txt"
    arquivo.write_text(WORKFLOW_EXEMPLO, encoding="utf-8")
    return arquivo


@pytest.fixture
def arquivo_sem_extensao(tmp_path: Path) -> Path:
    """Cria um arquivo sem extensão com conteúdo YAML válido."""
    arquivo = tmp_path / "workflow"
    arquivo.write_text(WORKFLOW_EXEMPLO, encoding="utf-8")
    return arquivo


@pytest.fixture
def workflow_exemplo_dict() -> dict[str, Any]:
    """Retorna o workflow de exemplo como dicionário Python"""
    return {
        "estados": {
            "aberto": {
                "acoes": {
                    "aprovar": {
                        "proximo_estado": "aprovado",
                        "terminal": False,
                    },
                    "rejeitar": {
                        "proximo_estado": "rejeitado",
                        "terminal": True,
                    },
                }
            },
            "aprovado": {
                "acoes": {
                    "iniciar_execucao": {
                        "proximo_estado": "em_execucao",
                        "terminal": False,
                    }
                }
            },
            "em_execucao": {
                "acoes": {
                    "finalizar": {
                        "proximo_estado": "concluido",
                        "terminal": True,
                    }
                }
            },
            "rejeitado": {"acoes": None},
            "concluido": {"acoes": None},
        }
    }


@pytest.fixture
def configurador() -> ConfiguradorWorkflow:
    """Instância reutilizável do configurador para os testes."""
    return ConfiguradorWorkflow()


@pytest.fixture
def leitor() -> LeitorWorkflow:
    """Instância reutilizável do leitor para os testes."""
    return LeitorWorkflow()


@pytest.fixture
def validador() -> ValidadorWorkflow:
    """Instância reutilizável do validador para os testes."""
    return ValidadorWorkflow()


@pytest.fixture
def dados_resultado() -> dict[str, object]:
    """Retorna os dados válidos padrão para criar um resultado."""
    inicio = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    return {
        "identificador": "execucao-123",
        "estado_anterior": "aberto",
        "acao": "aprovar",
        "proximo_estado": "aprovado",
        "terminal": True,
        "sucesso": True,
        "mensagem": "Solicitação aprovada com sucesso.",
        "inicio": inicio,
        "fim": inicio + timedelta(minutes=1),
        "autor": "usuario_1",
        "contexto": ContextoExecucao(autor="usuario_1"),
    }


@pytest.fixture(params=VALORES_INVALIDOS_IDENTIFICADOR)
def valor_invalido(request: pytest.FixtureRequest) -> Any:
    """Fornece cada valor inválido de identificador, um por teste."""
    return request.param


@pytest.fixture(params=VALORES_VALIDOS_IDENTIFICADOR)
def valor_valido(request: pytest.FixtureRequest) -> Any:
    """Fornece cada valor válido de identificador, um por teste."""
    return request.param


@pytest.fixture
def estados() -> dict[str, Estado]:
    """Retorna estados válidos para os testes."""
    return {
        "aberto": Estado(
            nome="aberto",
            acoes={
                "aprovar": Acao(
                    nome="aprovar",
                    proximo_estado="aprovado",
                    terminal=True,
                ),
                "rejeitar": Acao(
                    nome="rejeitar",
                    proximo_estado="rejeitado",
                    terminal=True,
                ),
                "enviar_para_analise": Acao(
                    nome="enviar_para_analise",
                    proximo_estado="em_analise",
                    terminal=False,
                ),
            },
        ),
        "em_analise": Estado(
            nome="em_analise",
            acoes={
                "aprovar": Acao(
                    nome="aprovar",
                    proximo_estado="aprovado",
                    terminal=True,
                ),
            },
        ),
        "aprovado": Estado(nome="aprovado", acoes=None),
        "rejeitado": Estado(nome="rejeitado", acoes=None),
    }


@pytest.fixture
def resolvedor(estados: dict[str, Estado]) -> DecisaoResolver:
    """Instância reutilizável do resolvedor para os testes.."""
    return DecisaoResolver(estados)


@pytest.fixture
def acao() -> Acao:
    """Retorna uma ação válida para os testes."""
    return Acao(
        nome="aprovar",
        proximo_estado="aprovado",
        terminal=True,
    )


@pytest.fixture
def motor(workflow_exemplo_dict: dict[str, Any]) -> MotorWorkflow:
    """Fornece um motor inicializado com a configuração de teste."""
    return MotorWorkflow(workflow_exemplo_dict)


@pytest.fixture
def contexto() -> ContextoExecucao:
    """Fornece um contexto de execução."""
    return ContextoExecucao(
        identificador="execucao-123",
        autor="usuario-teste",
        dados={"origem": "teste"},
    )


@pytest.fixture
def resultado_workflow(contexto: ContextoExecucao) -> ResultadoWorkflow:
    """Cria um resultado de workflow válido."""
    inicio = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
    fim = datetime(2026, 10, 27, 12, 1, tzinfo=UTC)

    return ResultadoWorkflow(
        identificador=contexto.identificador,
        estado_anterior="aberto",
        acao="aprovar",
        proximo_estado="aprovado",
        terminal=False,
        sucesso=True,
        mensagem="Transição executada com sucesso!",
        inicio=inicio,
        fim=fim,
        autor=contexto.autor,
        contexto=contexto,
    )
