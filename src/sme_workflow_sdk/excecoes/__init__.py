"""Exceções específicas do SDK."""

from sme_workflow_sdk.excecoes.base import (
    LeitorWorkflowError,
    ValidadorWorkflowError,
)
from sme_workflow_sdk.excecoes.configuracao import (
    ArquivoNaoEncontradoError,
    ConfiguracaoInvalidaError,
    EstadoInvalidoError,
    FormatoInvalidoError,
)

__all__ = [
    "LeitorWorkflowError",
    "ArquivoNaoEncontradoError",
    "ConfiguracaoInvalidaError",
    "FormatoInvalidoError",
    "EstadoInvalidoError",
    "ValidadorWorkflowError",
]
