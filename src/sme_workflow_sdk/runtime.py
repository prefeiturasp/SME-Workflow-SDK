"""Gerencia o ciclo de vida do runtime do SDK de workflow.

Este módulo é responsável por inicializar, disponibilizar e encerrar
a instância do motor de workflow utilizada pela aplicação consumidora.

O runtime mantém uma instância compartilhada do motor durante o ciclo
de vida da aplicação, evitando inicializações desnecessárias.

Principais responsabilidades:
    - Inicializar o motor de workflow a partir de um arquivo YAML.
    - Garantir a inicialização única do runtime.
    - Disponibilizar a instância configurada do motor.
    - Permitir o encerramento do runtime.
    - Registrar logs das operações de inicialização e encerramento.

Funções públicas:
    configure: Inicializa o runtime com o arquivo de configuração.
    get_workflow: Retorna a instância configurada do motor.
    shutdown: Encerra o runtime e libera a instância compartilhada.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.configuracao.configurador import ConfiguradorWorkflow

logger = logging.getLogger(__name__)


@dataclass
class RuntimeContext:
    """Armazena o estado da instância do SDK."""

    caminho: Path
    workflow: MotorWorkflow


_RUNTIME_CONTEXT: RuntimeContext | None = None


def configure(caminho: str | Path) -> None:
    """Inicializa o runtime do SDK com um arquivo de configuração.

    A inicialização é idempotente para o mesmo caminho. Caso o runtime
    já esteja inicializado com outro caminho, uma exceção será lançada.

    Args:
        caminho: Caminho do arquivo YAML de configuração.

    Raises:
        RuntimeError: Se o runtime já estiver configurado com outro caminho.
    """
    global _RUNTIME_CONTEXT

    caminho = Path(caminho).resolve()

    if _RUNTIME_CONTEXT is not None:
        if _RUNTIME_CONTEXT.caminho == caminho:
            logger.debug(
                "Workflow já inicializado com a configuração: %s",
                caminho,
            )
            return
        logger.error(
            "Tentativa de inicializar o workflow com outra configuração: %s",
            caminho,
        )
        raise RuntimeError(
            "O runtime do workflow já está inicializado com outra "
            "configuração."
        )

    try:
        configurador = ConfiguradorWorkflow()
        configuracao = configurador.carregar(str(caminho))
        workflow = MotorWorkflow(configuracao)

        _RUNTIME_CONTEXT = RuntimeContext(
            caminho=caminho,
            workflow=workflow,
        )

        logger.info("SDK de workflow inicializado com sucesso.")

    except Exception:
        logger.exception(
            "Falha ao inicializar o SDK de workflow. Configuração: %s",
            caminho,
        )
        raise


def get_workflow() -> MotorWorkflow:
    """Retorna a instância global do motor de workflow.

    Raises:
        RuntimeError: Se o runtime ainda não foi inicializado.
    """
    if _RUNTIME_CONTEXT is None:
        raise RuntimeError("O runtime do workflow ainda não foi inicializado.")

    return _RUNTIME_CONTEXT.workflow


def shutdown() -> None:
    """Encerra o runtime e libera a instância registrada."""
    global _RUNTIME_CONTEXT

    if _RUNTIME_CONTEXT is None:
        logger.debug("Solicitação de encerramento ignorada: runtime inativo.")
        return

    logger.info("Encerrando SDK de workflow.")

    _RUNTIME_CONTEXT = None

    logger.info("SDK de workflow encerrado.")
