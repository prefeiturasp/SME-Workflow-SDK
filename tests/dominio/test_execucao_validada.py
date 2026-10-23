"""Testes unitários para ExecucaoValidada."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from typing import cast

import pytest

from sme_workflow_sdk.dominio.entidades import Acao
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import ValidacaoDominioError


class TestExecucaoValidada:
    """Testes de criação e validação da execução."""

    def test_cria_execucao_com_valores_validos(self, acao: Acao) -> None:
        """Deve criar a execução com os dados informados."""
        inicio = datetime(2026, 10, 22, 15, 0, tzinfo=UTC)

        execucao = ExecucaoValidada(
            estado_atual="pendente",
            acao=acao,
            inicio_transicao=inicio,
        )

        assert execucao.estado_atual == "pendente"
        assert execucao.acao is acao
        assert execucao.inicio_transicao == inicio

    def test_define_inicio_automaticamente(self, acao: Acao) -> None:
        """Deve definir o início quando ele não for informado."""
        antes = datetime.now(UTC)

        execucao = ExecucaoValidada(
            estado_atual="pendente",
            acao=acao,
        )

        depois = datetime.now(UTC)

        assert antes <= execucao.inicio_transicao <= depois
        assert execucao.inicio_transicao.tzinfo is not None

    @pytest.mark.parametrize("estado", ["", "   "])
    def test_rejeita_estado_vazio(self, acao: Acao, estado: str) -> None:
        """Não deve aceitar um estado vazio."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ExecucaoValidada(estado_atual=estado, acao=acao)

        assert (
            str(exc.value)
            == "ExecucaoValidada.estado_atual não pode ser vazio"
        )

    def test_rejeita_estado_invalido(
        self, acao: Acao, valor_invalido: str
    ) -> None:
        """Não deve aceitar um estado invalido."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ExecucaoValidada(estado_atual=valor_invalido, acao=acao)

        assert (
            f"ExecucaoValidada.estado_atual inválido ('{valor_invalido}'). O "
            "valor deve conter apenas letras e sublinhados ('_') entre "
            "palavras (ex.: 'em_execucao'). Não são permitidos sublinhados no "
            "início, no fim ou duplicados." in str(exc.value)
        )

    def test_rejeita_acao_com_tipo_invalido(self) -> None:
        """Deve rejeitar um objeto que não seja uma instância de Acao."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ExecucaoValidada(
                estado_atual="pendente",
                acao=cast(Acao, "aprovar"),
            )

        assert (
            str(exc.value)
            == "ExecucaoValidada.acao deve ser uma instância de Acao."
        )

    def test_rejeita_inicio_que_nao_seja_datetime(self, acao: Acao) -> None:
        """Deve rejeitar um início que não seja datetime."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ExecucaoValidada(
                estado_atual="pendente",
                acao=acao,
                inicio_transicao=cast(datetime, "2026-10-22"),
            )

        assert (
            str(exc.value)
            == "ExecucaoValidada.inicio_transicao deve ser uma instância "
            "de datetime."
        )

    def test_rejeita_inicio_sem_fuso_horario(self, acao: Acao) -> None:
        """Deve exigir um datetime com fuso horário."""
        inicio = datetime(2026, 10, 22, 15, 0)

        with pytest.raises(ValidacaoDominioError) as exc:
            ExecucaoValidada(
                estado_atual="pendente",
                acao=acao,
                inicio_transicao=inicio,
            )

        assert (
            str(exc.value)
            == "ExecucaoValidada.inicio_transicao deve possuir fuso "
            "horário definido."
        )

    def test_nao_permite_alterar_execucao(self, acao: Acao) -> None:
        """A execução deve ser imutável após a criação."""
        execucao = ExecucaoValidada(
            estado_atual="pendente",
            acao=acao,
        )

        atributo = "estado_atual"

        with pytest.raises(FrozenInstanceError):
            setattr(execucao, atributo, "aprovado")
