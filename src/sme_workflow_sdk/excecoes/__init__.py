"""Exceções específicas do SDK."""

from sme_workflow_sdk.excecoes.base import LeitorWorkflowError
from sme_workflow_sdk.excecoes.configuracao import (
    ArquivoNaoEncontradoError,
    ConfiguracaoInvalidaError,
    FormatoInvalidoError,
)

__all__ = [
    "LeitorWorkflowError",
    "ArquivoNaoEncontradoError",
    "ConfiguracaoInvalidaError",
    "FormatoInvalidoError",
]
