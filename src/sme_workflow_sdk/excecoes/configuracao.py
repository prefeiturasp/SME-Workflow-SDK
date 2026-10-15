"""Exceções relacionadas à configuração do workflow."""

from sme_workflow_sdk.excecoes.base import (
    LeitorWorkflowError,
    ValidadorWorkflowError,
)


class ArquivoNaoEncontradoError(LeitorWorkflowError):
    """Arquivo inexistente ou inacessível."""


class FormatoInvalidoError(LeitorWorkflowError):
    """Extensão ou estrutura do arquivo inválida."""


class ConfiguracaoInvalidaError(LeitorWorkflowError):
    """Conteúdo da configuração inválido."""


class EstadoInvalidoError(ValidadorWorkflowError):
    """Conteúdo da configuração inválido."""


class AcaoInvalidaError(ValidadorWorkflowError):
    """Conteúdo da configuração inválido."""
