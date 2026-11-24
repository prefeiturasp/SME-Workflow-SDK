"""Recursos de integração declarativa do SDK."""

from sme_workflow_sdk.integracao.decorators import workflow
from sme_workflow_sdk.integracao.registro_acoes import (
    RegistroAcoes,
    registro_acoes,
)

__all__ = ["RegistroAcoes", "registro_acoes", "workflow"]
