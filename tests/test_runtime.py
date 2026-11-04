"""Testes do gerenciamento do runtime do SDK."""

from pathlib import Path
from unittest.mock import patch

import pytest

from sme_workflow_sdk import runtime
from sme_workflow_sdk.configuracao.configurador import (
    ConfiguradorWorkflow,
)


class TestRuntime:
    def test_configure_deve_inicializar_runtime(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve carregar a configuração e inicializar o motor."""
        caminho = tmp_path / "workflow.yaml"

        with (
            patch.object(
                ConfiguradorWorkflow,
                "carregar",
                return_value={"estados": {}},
            ) as carregar,
            patch.object(
                runtime,
                "MotorWorkflow",
            ) as motor,
        ):
            runtime.configure(caminho)

            carregar.assert_called_once_with(str(caminho.resolve()))
            motor.assert_called_once_with({"estados": {}})

            assert runtime.get_workflow() is motor.return_value

    def test_configure_deve_reutilizar_instancia_para_mesmo_caminho(
        self,
        tmp_path: Path,
    ) -> None:
        """Não deve criar outro motor para o mesmo caminho."""
        caminho = tmp_path / "workflow.yaml"

        with (
            patch.object(
                ConfiguradorWorkflow,
                "carregar",
                return_value={"estados": {}},
            ) as carregar,
            patch.object(runtime, "MotorWorkflow") as motor,
        ):
            runtime.configure(caminho)
            workflow = runtime.get_workflow()

            runtime.configure(caminho)

            assert runtime.get_workflow() is workflow
            carregar.assert_called_once()
            motor.assert_called_once()

    def test_configure_deve_rejeitar_outro_caminho(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve impedir a substituição silenciosa da configuração."""
        primeiro_caminho = tmp_path / "workflow.yaml"
        segundo_caminho = tmp_path / "outro_workflow.yaml"

        with (
            patch.object(
                ConfiguradorWorkflow,
                "carregar",
                return_value={"estados": {}},
            ),
            patch.object(runtime, "MotorWorkflow"),
        ):
            runtime.configure(primeiro_caminho)

            with pytest.raises(RuntimeError, match="outra configuração"):
                runtime.configure(segundo_caminho)

    def test_configure_deve_manter_runtime_nao_inicializado_se_falhar(
        self,
        tmp_path: Path,
    ) -> None:
        """Não deve registrar o runtime quando o carregamento falhar."""
        caminho = tmp_path / "workflow.yaml"

        with (
            patch.object(
                ConfiguradorWorkflow,
                "carregar",
                side_effect=ValueError("Configuração inválida"),
            ),
            pytest.raises(ValueError, match="Configuração inválida"),
        ):
            runtime.configure(caminho)

        with pytest.raises(RuntimeError, match="ainda não foi inicializado"):
            runtime.get_workflow()

    def test_get_workflow_deve_lancar_erro_quando_nao_inicializado(
        self,
    ) -> None:
        """Deve impedir o acesso ao motor antes da inicialização."""
        with pytest.raises(RuntimeError, match="ainda não foi inicializado"):
            runtime.get_workflow()

    def test_shutdown_deve_limpar_runtime(
        self,
        tmp_path: Path,
    ) -> None:
        """Deve remover a instância registrada."""
        caminho = tmp_path / "workflow.yaml"

        with (
            patch.object(
                ConfiguradorWorkflow,
                "carregar",
                return_value={"estados": {}},
            ),
            patch.object(runtime, "MotorWorkflow"),
        ):
            runtime.configure(caminho)
            runtime.shutdown()

        with pytest.raises(RuntimeError, match="ainda não foi inicializado"):
            runtime.get_workflow()
