"""Exceções relacionadas à configuração do workflow."""

from sme_workflow_sdk.excecoes.base import LeitorWorkflowError


class ArquivoNaoEncontradoError(LeitorWorkflowError):
    """Arquivo inexistente ou inacessível."""


class FormatoInvalidoError(LeitorWorkflowError):
    """Extensão ou estrutura do arquivo inválida."""


class ConfiguracaoInvalidaError(LeitorWorkflowError):
    """Conteúdo da configuração inválido."""
