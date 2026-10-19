"""Entidades do domínio do SME Workflow SDK."""

from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.entidades import Acao, Estado, Transicao
from sme_workflow_sdk.dominio.resultado import ResultadoWorkflow

__all__ = [
    "Acao",
    "ContextoExecucao",
    "Estado",
    "Transicao",
    "ResultadoWorkflow",
]
