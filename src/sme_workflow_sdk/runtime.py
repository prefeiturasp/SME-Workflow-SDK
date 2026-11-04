"""_summary_."""

from dataclasses import dataclass
from pathlib import Path

from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.configuracao.configurador import ConfiguradorWorkflow


@dataclass
class _EstadoRuntime:
    """Armazena o estado da instância do SDK."""

    caminho: Path
    workflow: MotorWorkflow


_ESTADO: _EstadoRuntime | None = None


def configure(caminho: str | Path) -> None:
    """Inicializa o runtime do SDK com um arquivo de configuração.

    A inicialização é idempotente para o mesmo caminho. Caso o runtime
    já esteja inicializado com outro caminho, uma exceção será lançada.

    Args:
        caminho: Caminho do arquivo YAML de configuração.

    Raises:
        RuntimeError: Se o runtime já estiver configurado com outro caminho.
    """
    global _ESTADO

    caminho = Path(caminho).resolve()

    if _ESTADO is not None:
        if _ESTADO.caminho == caminho:
            return

        raise RuntimeError(
            "O runtime do workflow já está inicializado com outra "
            "configuração."
        )

    configurador = ConfiguradorWorkflow()
    configuracao = configurador.carregar(str(caminho))
    workflow = MotorWorkflow(configuracao)

    _ESTADO = _EstadoRuntime(
        caminho=caminho,
        workflow=workflow,
    )
