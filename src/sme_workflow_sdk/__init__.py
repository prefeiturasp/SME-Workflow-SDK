"""SDK para gerenciamento de workflows e transições de estado."""

from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.configuracao.configurador import ConfiguradorWorkflow
from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.dominio.resultado import ResultadoWorkflow

__all__ = [
    "ConfiguradorWorkflow",
    "ContextoExecucao",
    "ExecucaoValidada",
    "MotorWorkflow",
    "ResultadoWorkflow",
]
