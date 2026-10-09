from typing import Any

import pytest

from sme_workflow_sdk.configuracao.validador import ValidadorWorkflow


@pytest.fixture
def validador() -> ValidadorWorkflow:
    """Retorna uma instância do validador."""
    return ValidadorWorkflow()


@pytest.fixture
def configuracao_valida() -> dict[str, Any]:
    """Retorna uma configuração válida de workflow."""
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
                    "finalizar": {
                        "proximo_estado": "concluido",
                        "terminal": True,
                    }
                }
            },
            "rejeitado": {"acoes": {}},
            "concluido": {"acoes": {}},
        }
    }
