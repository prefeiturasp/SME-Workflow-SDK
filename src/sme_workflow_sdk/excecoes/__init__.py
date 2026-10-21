"""Exceções específicas do SDK."""

from sme_workflow_sdk.excecoes.base import (
    LeitorWorkflowError,
    ValidacaoDominioError,
    ValidadorWorkflowError,
)
from sme_workflow_sdk.excecoes.configuracao import (
    AcaoInvalidaError,
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
    "AcaoInvalidaError",
    "ValidacaoDominioError",
]
