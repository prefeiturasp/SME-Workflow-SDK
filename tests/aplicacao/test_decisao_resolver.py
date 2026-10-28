"""Testes unitários do decisao_resolver de decisões do workflow."""

import pytest

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.dominio.entidades import Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import AcaoInvalidaError, EstadoInvalidoError


class TestDecisaoResolver:
    def test_deve_validar_estado_e_acao_permitidos(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Não deve lançar exceção para uma ação permitida."""
        decisao_resolver.validar("aberto", "aprovar")

    def test_valida_acao_e_retorna_execucao_validada(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve retornar a execução validada para uma ação permitida."""
        resultado = decisao_resolver.validar("aberto", "rejeitar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"
        assert resultado.acao.nome == "rejeitar"
        assert resultado.acao.proximo_estado == "rejeitado"
        assert resultado.acao.terminal is True

    def test_deve_lancar_excecao_para_estado_inexistente(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve rejeitar um estado que não existe."""
        with pytest.raises(EstadoInvalidoError) as exc:
            decisao_resolver.validar("inexistente", "aprovar")

        assert str(exc.value) == (
            "O estado 'inexistente' não existe no arquivo de configuração."
        )

    def test_deve_lancar_excecao_para_acao_nao_permitida(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve rejeitar uma ação não configurada para o estado."""
        with pytest.raises(AcaoInvalidaError) as exc:
            decisao_resolver.validar("aberto", "iniciar_execucao")

        assert str(exc.value) == (
            "A ação 'iniciar_execucao' não é permitida no estado 'aberto'."
        )

    def test_deve_lancar_excecao_para_estado_sem_acoes(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve rejeitar ações em um estado sem ações disponíveis."""
        with pytest.raises(AcaoInvalidaError) as exc:
            decisao_resolver.validar("aprovado", "aprovar")

        assert str(exc.value) == (
            "A ação 'aprovar' não é permitida no estado 'aprovado'."
        )


class TestDecisaoResolverInicializacao:
    """Testes da inicialização do decisao_resolver."""

    def test_inicializa_com_configuracao_vazia(self) -> None:
        """Deve aceitar um mapeamento vazio na inicialização."""
        resolver = DecisaoResolver(estados={})

        with pytest.raises(EstadoInvalidoError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O estado 'aberto' não existe no arquivo de configuração."
        )

    def test_inicializa_com_varios_estados(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve aceitar uma configuração com vários estados."""
        resolver = DecisaoResolver(estados)

        resultado = resolver.validar("em_analise", "aprovar")

        assert resultado.estado_atual == "em_analise"
        assert resultado.acao.nome == "aprovar"


class TestDecisaoResolverValidacaoEstado:
    """Testes da validação do estado atual."""

    def test_aceita_estado_existente(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve aceitar um estado existente na configuração."""
        resultado = decisao_resolver.validar("aberto", "aprovar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"

    @pytest.mark.parametrize(
        "estado_atual",
        ["inexistente", "pendente", "ABERTO"],
    )
    def test_rejeita_estado_inexistente(
        self,
        decisao_resolver: DecisaoResolver,
        estado_atual: str,
    ) -> None:
        """Deve rejeitar estados que não estejam configurados."""
        with pytest.raises(EstadoInvalidoError) as exc:
            decisao_resolver.validar(estado_atual, "aprovar")

        assert (
            str(exc.value)
            == f"O estado '{estado_atual}' não existe no arquivo de "
            "configuração."
        )

    def test_valida_estado_antes_da_acao(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve informar o erro de estado antes de validar a ação."""
        with pytest.raises(EstadoInvalidoError) as exc:
            decisao_resolver.validar("inexistente", "acao_inexistente")

        assert (
            str(exc.value)
            == "O estado 'inexistente' não existe no arquivo de configuração."
        )


class TestDecisaoResolverValidacaoAcao:
    """Testes da disponibilidade de ações."""

    def test_aceita_acao_configurada(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve aceitar uma ação disponível no estado atual."""
        resultado = decisao_resolver.validar("aberto", "aprovar")

        assert resultado.acao.nome == "aprovar"
        assert resultado.acao.proximo_estado == "aprovado"
        assert resultado.acao.terminal is True

    def test_retorna_a_entidade_acao_configurada(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve preservar a entidade de ação presente na configuração."""
        acoes = estados["aberto"].acoes
        assert acoes is not None
        acao = acoes["aprovar"]
        resolver = DecisaoResolver(estados)

        resultado = resolver.validar("aberto", "aprovar")

        assert resultado.acao is acao

    @pytest.mark.parametrize(
        "nome_acao",
        ["cancelar", "excluir", "aprovar "],
    )
    def test_rejeita_acao_nao_configurada(
        self,
        decisao_resolver: DecisaoResolver,
        nome_acao: str,
    ) -> None:
        """Deve rejeitar ações que não estejam disponíveis."""
        with pytest.raises(AcaoInvalidaError) as exc:
            decisao_resolver.validar("aberto", nome_acao)

        assert (
            str(exc.value)
            == f"A ação '{nome_acao}' não é permitida no estado 'aberto'."
        )

    @pytest.mark.parametrize(
        "estado_atual",
        ["aprovado", "rejeitado"],
    )
    def test_rejeita_acao_em_estado_sem_acoes(
        self,
        decisao_resolver: DecisaoResolver,
        estado_atual: str,
    ) -> None:
        """Deve rejeitar ações quando o estado possui acoes=None."""
        with pytest.raises(AcaoInvalidaError) as exc:
            decisao_resolver.validar(estado_atual, "aprovar")

        assert (
            str(exc.value)
            == f"A ação 'aprovar' não é permitida no estado '{estado_atual}'."
        )

    def test_rejeita_acao_com_mapeamento_vazio(
        self,
    ) -> None:
        """Deve rejeitar ações quando o estado possui um mapeamento vazio."""
        resolver = DecisaoResolver({"aberto": Estado(nome="aberto", acoes={})})

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "A ação 'aprovar' não é permitida no estado 'aberto'."
        )


class TestDecisaoResolverIndependencia:
    """Testes para garantir que cada validação usa os dados recebidos."""

    def test_valida_acoes_de_estados_diferentes(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Deve resolver corretamente ações em estados diferentes."""
        primeira = decisao_resolver.validar("aberto", "enviar_para_analise")
        segunda = decisao_resolver.validar("em_analise", "aprovar")

        assert primeira.estado_atual == "aberto"
        assert primeira.acao.nome == "enviar_para_analise"
        assert primeira.acao.proximo_estado == "em_analise"

        assert segunda.estado_atual == "em_analise"
        assert segunda.acao.nome == "aprovar"
        assert segunda.acao.proximo_estado == "aprovado"

    def test_erro_em_uma_validacao_nao_afeta_a_seguinte(
        self,
        decisao_resolver: DecisaoResolver,
    ) -> None:
        """Uma validação inválida não deve impedir uma válida posterior."""
        with pytest.raises(EstadoInvalidoError):
            decisao_resolver.validar("inexistente", "aprovar")

        resultado = decisao_resolver.validar("aberto", "aprovar")

        assert resultado.estado_atual == "aberto"
        assert resultado.acao.nome == "aprovar"
