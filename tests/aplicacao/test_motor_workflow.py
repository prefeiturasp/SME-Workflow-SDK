from typing import Any

from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.dominio.entidades import Acao, Estado


class TestMotorWorkflowInicializacao:
    """Testes da inicialização e conversão da configuração."""

    def test_inicializa_com_configuracao_valida(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve inicializar o motor com uma configuração válida."""
        assert isinstance(motor, MotorWorkflow)

    def test_converte_estados_da_configuracao(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve converter os estados configurados em entidades de domínio."""
        estados = motor._estados

        assert set(estados) == {
            "aberto",
            "aprovado",
            "em_execucao",
            "rejeitado",
            "concluido",
        }
        assert isinstance(estados["aberto"], Estado)
        assert estados["aberto"].nome == "aberto"

    def test_converte_acoes_da_configuracao(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve converter ações em entidades Acao."""
        acoes = motor._estados["aberto"].acoes

        assert acoes is not None
        assert isinstance(acoes["aprovar"], Acao)
        assert acoes["aprovar"].nome == "aprovar"
        assert acoes["aprovar"].proximo_estado == "aprovado"
        assert acoes["aprovar"].terminal is False

    def test_preserva_estado_sem_acoes(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve preservar acoes=None em estados sem ações."""
        assert motor._estados["rejeitado"].acoes is None
        assert motor._estados["concluido"].acoes is None

    def test_converte_configuracao_sem_estados(self) -> None:
        """Deve retornar um dicionário vazio sem estados configurados."""
        estados = MotorWorkflow._converter_estados({"estados": {}})

        assert estados == {}

    def test_converte_estado_com_acoes_vazias(self) -> None:
        """Deve preservar um mapeamento de ações vazio."""
        workflow_exemplo_dict: dict[str, Any] = {
            "estados": {
                "aberto": {
                    "acoes": {},
                },
            },
        }
        estados = MotorWorkflow._converter_estados(workflow_exemplo_dict)

        assert estados["aberto"].acoes == {}

    def test_converte_multiplas_acoes_do_mesmo_estado(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve preservar todas as ações configuradas para um estado."""
        acoes = motor._estados["aberto"].acoes

        assert acoes is not None
        assert set(acoes) == {"aprovar", "rejeitar"}

    def test_preserva_destinos_e_indicadores_das_acoes(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve preservar os destinos e indicadores das ações."""
        acoes = motor._estados["aberto"].acoes

        assert acoes is not None
        assert acoes["aprovar"].proximo_estado == "aprovado"
        assert acoes["aprovar"].terminal is False
        assert acoes["rejeitar"].proximo_estado == "rejeitado"
        assert acoes["rejeitar"].terminal is True

    def test_conversoes_criam_novas_entidades(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Chamadas distintas devem criar novas entidades de estado."""
        primeira = MotorWorkflow._converter_estados(workflow_exemplo_dict)
        segunda = MotorWorkflow._converter_estados(workflow_exemplo_dict)

        assert primeira["aberto"] == segunda["aberto"]
        assert primeira["aberto"] is not segunda["aberto"]

    def test_instancias_do_motor_nao_compartilham_estados(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Motores distintos devem criar suas próprias entidades."""
        primeiro_motor = MotorWorkflow(workflow_exemplo_dict)
        segundo_motor = MotorWorkflow(workflow_exemplo_dict)

        assert (
            primeiro_motor._estados["aberto"]
            is not segundo_motor._estados["aberto"]
        )
