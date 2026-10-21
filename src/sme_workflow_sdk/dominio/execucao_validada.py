"""Contrato de uma execução de workflow validada."""

from dataclasses import dataclass

from sme_workflow_sdk.dominio.entidades import Acao


@dataclass(frozen=True, slots=True)
class ExecucaoValidada:
    """Representa uma ação validada, aguardando execução."""

    estado_atual: str
    acao: Acao
