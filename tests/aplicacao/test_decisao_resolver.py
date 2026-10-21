"""Testes unitários do resolvedor de decisões do workflow."""

import pytest

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.excecoes import AcaoInvalidaError, EstadoInvalidoError


class TestDecisaoResolver:
    def test_deve_validar_estado_e_acao_permitidos(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Não deve lançar exceção para uma ação permitida."""
        resolvedor.validar("aberto", "aprovar")

    def test_deve_lancar_excecao_para_estado_inexistente(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve rejeitar um estado que não existe."""
        with pytest.raises(EstadoInvalidoError) as exc:
            resolvedor.validar("inexistente", "aprovar")

        assert str(exc.value) == (
            "O estado 'inexistente' não existe na configuração."
        )

    def test_deve_lancar_excecao_para_acao_nao_permitida(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve rejeitar uma ação não configurada para o estado."""
        with pytest.raises(AcaoInvalidaError) as exc:
            resolvedor.validar("aberto", "iniciar_execucao")

        assert str(exc.value) == (
            "A ação 'iniciar_execucao' não é permitida no estado 'aberto'."
        )

    def test_deve_lancar_excecao_para_estado_sem_acoes(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve rejeitar ações em um estado sem ações disponíveis."""
        with pytest.raises(AcaoInvalidaError) as exc:
            resolvedor.validar("aprovado", "aprovar")

        assert str(exc.value) == (
            "A ação 'aprovar' não é permitida no estado 'aprovado'."
        )
