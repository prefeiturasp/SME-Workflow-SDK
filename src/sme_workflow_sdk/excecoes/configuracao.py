"""Exceções relacionadas à leitura e validação da configuração do workflow."""

from sme_workflow_sdk.excecoes.base import (
    LeitorWorkflowError,
    ValidadorWorkflowError,
)


class ArquivoNaoEncontradoError(LeitorWorkflowError):
    """Indica que o arquivo de configuração não foi encontrado ou acessado."""


class FormatoInvalidoError(LeitorWorkflowError):
    """Indica que o arquivo possui extensão ou estrutura YAML inválida."""


class ConfiguracaoInvalidaError(LeitorWorkflowError):
    """Indica que o conteúdo YAML não possui uma estrutura válida."""


class EstadoInvalidoError(ValidadorWorkflowError):
    """Indica que um estado possui nome, estrutura ou referência inválida."""


class AcaoInvalidaError(ValidadorWorkflowError):
    """Indica que uma ação possui nome, estrutura ou transição inválida."""
