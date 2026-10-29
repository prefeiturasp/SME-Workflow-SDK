"""Testes do resolvedor de transições do workflow."""

from datetime import UTC, datetime
from typing import Any

import pytest

from sme_workflow_sdk.aplicacao.transicao_resolver import TransicaoResolver
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import TransicaoInvalidaError


@pytest.fixture
def resolver(estados: dict[str, Estado]) -> TransicaoResolver:
    """Cria o resolvedor com os estados de teste."""
    return TransicaoResolver(estados)


def criar_execucao(
    *,
    estado_atual: str = "aberto",
    nome_acao: str = "aprovar",
    proximo_estado: str = "aprovado",
    terminal: bool = False,
) -> ExecucaoValidada:
    """Cria uma execução validada para testar a resolução da transição."""
    acao = Acao(
        nome=nome_acao,
        proximo_estado=proximo_estado,
        terminal=terminal,
    )
    return ExecucaoValidada(
        estado_atual=estado_atual,
        acao=acao,
        inicio_transicao=datetime(2026, 10, 28, 12, 0, tzinfo=UTC),
    )


class TestTransicaoResolver:
    """Testes da validação e resolução das transições."""

    def test_retorna_execucao_quando_destino_existe(
        self,
        resolver: TransicaoResolver,
    ) -> None:
        """Deve aceitar uma transição cujo destino esteja configurado."""
        execucao = criar_execucao()

        resultado = resolver.resolver(execucao)

        assert resultado is execucao
        assert resultado.estado_atual == "aberto"
        assert resultado.acao.proximo_estado == "aprovado"

    def test_rejeita_proximo_estado_inexistente(
        self,
        resolver: TransicaoResolver,
    ) -> None:
        """Deve rejeitar uma transição para um estado não configurado."""
        execucao = criar_execucao(proximo_estado="inexistente")

        with pytest.raises(
            TransicaoInvalidaError,
            match="próximo estado 'inexistente'.*não existe",
        ):
            resolver.resolver(execucao)

    def test_rejeita_transicao_nao_terminal_para_mesmo_estado(
        self,
        resolver: TransicaoResolver,
    ) -> None:
        """Deve rejeitar retorno ao mesmo estado quando não for terminal."""
        execucao = criar_execucao(
            proximo_estado="aberto",
            terminal=False,
        )

        with pytest.raises(
            TransicaoInvalidaError,
            match="não pode retornar ao mesmo estado",
        ):
            resolver.resolver(execucao)

    def test_permite_transicao_terminal_para_mesmo_estado(
        self,
        resolver: TransicaoResolver,
    ) -> None:
        """Deve permitir transição para o mesmo estado se for terminal."""
        execucao = criar_execucao(
            nome_acao="encerrar",
            proximo_estado="aberto",
            terminal=True,
        )

        resultado = resolver.resolver(execucao)

        assert resultado is execucao
        assert resultado.acao.terminal is True

    def test_nao_altera_execucao_original(
        self,
        resolver: TransicaoResolver,
    ) -> None:
        """A resolução não deve modificar os dados da execução."""
        execucao = criar_execucao()
        estado_atual = execucao.estado_atual
        acao = execucao.acao
        inicio = execucao.inicio_transicao

        resolver.resolver(execucao)

        assert execucao.estado_atual == estado_atual
        assert execucao.acao is acao
        assert execucao.inicio_transicao == inicio

    @pytest.mark.parametrize(
        "proximo_estado",
        [
            "",
            "   ",
            "\t",
            "\n",
            123,
            None,
        ],
    )
    def test_rejeita_proximo_estado_invalido(
        self,
        resolver: TransicaoResolver,
        proximo_estado: Any,
    ) -> None:
        """Rejeita próximo estado vazio, com espaços ou tipo inválido."""
        acao = object.__new__(Acao)
        object.__setattr__(acao, "nome", "aprovar")
        object.__setattr__(acao, "proximo_estado", proximo_estado)
        object.__setattr__(acao, "terminal", False)

        execucao = ExecucaoValidada(
            estado_atual="aberto",
            acao=acao,
            inicio_transicao=datetime(2026, 10, 28, 12, 0, tzinfo=UTC),
        )

        with pytest.raises(
            TransicaoInvalidaError,
            match="O próximo estado da ação 'aprovar' no estado 'aberto' é "
            "inválido.",
        ):
            resolver.resolver(execucao)

    @pytest.mark.parametrize(
        "terminal",
        [
            "sim",
            1,
            None,
            [],
        ],
    )
    def test_rejeita_terminal_com_tipo_invalido(
        self,
        resolver: TransicaoResolver,
        terminal: Any,
    ) -> None:
        """Rejeita o campo terminal quando não for booleano."""
        acao = object.__new__(Acao)
        object.__setattr__(acao, "nome", "aprovar")
        object.__setattr__(acao, "proximo_estado", "aprovado")
        object.__setattr__(acao, "terminal", terminal)

        execucao = ExecucaoValidada(
            estado_atual="aberto",
            acao=acao,
            inicio_transicao=datetime(2026, 10, 28, 12, 0, tzinfo=UTC),
        )

        with pytest.raises(
            TransicaoInvalidaError,
            match="O campo 'terminal' da ação 'aprovar' no estado 'aberto' "
            "deve ser booleano.",
        ):
            resolver.resolver(execucao)
