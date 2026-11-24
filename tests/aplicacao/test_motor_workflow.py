from datetime import UTC
from typing import Any

import pytest

from sme_workflow_sdk.aplicacao.motor_workflow import MotorWorkflow
from sme_workflow_sdk.dominio.contexto import ContextoExecucao
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes.configuracao import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


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


class TestMotorWorkflowValidacao:
    """Testes da validação de estados e ações."""

    def test_valida_acao_e_retorna_execucao_validada(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve retornar os dados validados da transição."""
        resultado = motor.validar("aberto", "aprovar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"
        assert resultado.acao.nome == "aprovar"
        assert resultado.acao.proximo_estado == "aprovado"
        assert resultado.acao.terminal is False

    def test_rejeita_estado_inexistente(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve propagar o erro quando o estado não existir."""
        with pytest.raises(EstadoInvalidoError) as exc:
            motor.validar("inexistente", "aprovar")

        assert (
            str(exc.value)
            == "O estado 'inexistente' não existe no arquivo de configuração."
        )

    def test_rejeita_acao_nao_configurada(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve propagar o erro quando a ação não estiver disponível."""
        with pytest.raises(AcaoInvalidaError) as exc:
            motor.validar("aberto", "cancelar")

        assert (
            str(exc.value)
            == "A ação 'cancelar' não é permitida no estado 'aberto'."
        )

    def test_valida_transicao_utilizando_configuracao(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve validar a transição conforme a configuração do workflow."""
        resultado = motor.validar("aberto", "aprovar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"
        assert resultado.acao.nome == "aprovar"
        assert resultado.acao.proximo_estado == "aprovado"
        assert resultado.acao.terminal is False

    def test_validacoes_sucessivas_nao_interferem_entre_si(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Cada validação deve devolver os dados da própria solicitação."""
        primeira = motor.validar("aberto", "aprovar")
        segunda = motor.validar("aberto", "rejeitar")

        assert primeira.estado_atual == "aberto"
        assert primeira.acao.nome == "aprovar"
        assert primeira.acao.proximo_estado == "aprovado"

        assert segunda.estado_atual == "aberto"
        assert segunda.acao.nome == "rejeitar"
        assert segunda.acao.proximo_estado == "rejeitado"

        assert primeira is not segunda


class TestMotorWorkflowExecucao:
    """Testes da montagem do resultado da execução."""

    def test_executa_transicao_com_sucesso(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve montar um resultado de sucesso para a transição."""

        resultado = motor.processar_transicao(
            estado="aberto", acao="aprovar", autor="Antonio"
        )
        assert "identificador" in resultado
        assert resultado["estado_anterior"] == "aberto"
        assert resultado["acao"] == "aprovar"
        assert resultado["proximo_estado"] == "aprovado"
        assert resultado["terminal"] is False
        assert resultado["sucesso"] is True
        assert resultado["inicio"].tzinfo == UTC
        assert resultado["fim"] >= resultado["inicio"]
        assert resultado["fim"].tzinfo == UTC
        assert resultado["autor"] == "Antonio"
        assert resultado["mensagem"] == "Transição processada com sucesso!"

    def test_executa_transicao_nao_terminal(
        self,
        motor: MotorWorkflow,
        contexto: ContextoExecucao,
    ) -> None:
        """Deve preservar o destino e o indicador de transição não terminal."""
        dados_transicao = motor.validar("aberto", "aprovar")

        resultado = motor.processar_transicao(
            estado=dados_transicao.estado_atual,
            acao=dados_transicao.acao.nome,
            autor=contexto.autor,
        )

        assert resultado["estado_anterior"] == "aberto"
        assert resultado["acao"] == "aprovar"
        assert resultado["proximo_estado"] == "aprovado"
        assert resultado["terminal"] is False
        assert resultado["sucesso"] is True

    def test_preserva_identificador_e_autor_do_contexto(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve utilizar os dados de identificação do contexto recebido."""
        dados_transicao = motor.validar("aberto", "aprovar")

        resultado = motor.processar_transicao(
            estado=dados_transicao.estado_atual,
            acao=dados_transicao.acao.nome,
            autor="Autor 0003",
        )

        assert "identificador" in resultado
        assert resultado["autor"] == "Autor 0003"

    def test_gera_datas_com_fuso_utc(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Deve gerar a data final com fuso UTC."""
        dados_transicao = motor.validar("aberto", "aprovar")

        resultado = motor.processar_transicao(
            estado=dados_transicao.estado_atual,
            acao=dados_transicao.acao.nome,
            autor="458631",
        )

        inicio = resultado["inicio"]
        fim = resultado["fim"]
        assert inicio.tzinfo == UTC
        assert fim.tzinfo == UTC
        assert fim >= inicio

    def test_execucoes_utilizam_contextos_independentes(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Execuções distintas devem manter seus próprios contextos."""
        dados_transicao = motor.validar("aberto", "aprovar")

        primeiro_resultado = motor.processar_transicao(
            estado=dados_transicao.estado_atual,
            acao=dados_transicao.acao.nome,
            autor="usuario-1",
        )
        segundo_resultado = motor.processar_transicao(
            estado=dados_transicao.estado_atual,
            acao=dados_transicao.acao.nome,
            autor="usuario-2",
        )

        assert primeiro_resultado["autor"] == "usuario-1"
        assert segundo_resultado["autor"] == "usuario-2"

    def test_nao_altera_a_execucao_validada(
        self,
        motor: MotorWorkflow,
    ) -> None:
        """Executar não deve modificar os dados previamente validados."""
        dados_transicao = motor.validar("aberto", "aprovar")
        estado_original = dados_transicao.estado_atual
        acao_original = dados_transicao.acao
        inicio_original = dados_transicao.inicio_transicao

        motor.processar_transicao(
            estado=estado_original,
            acao=acao_original.nome,
            autor="usuario-2",
        )

        assert dados_transicao.estado_atual == estado_original
        assert dados_transicao.acao is acao_original
        assert dados_transicao.inicio_transicao == inicio_original
