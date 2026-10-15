"""Fixtures compartilhadas para os testes."""

from pathlib import Path
from typing import Any

import pytest

from sme_workflow_sdk.configuracao import ConfiguradorWorkflow
from sme_workflow_sdk.configuracao.leitor import LeitorWorkflow
from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow

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
