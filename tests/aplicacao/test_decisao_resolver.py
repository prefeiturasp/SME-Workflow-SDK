"""Testes unitários do resolvedor de decisões do workflow."""

import pytest

from sme_workflow_sdk.aplicacao.decisao_resolver import DecisaoResolver
from sme_workflow_sdk.dominio.entidades import Acao, Estado
from sme_workflow_sdk.dominio.execucao_validada import ExecucaoValidada
from sme_workflow_sdk.excecoes import AcaoInvalidaError, EstadoInvalidoError


class TestDecisaoResolver:
    def test_deve_validar_estado_e_acao_permitidos(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Não deve lançar exceção para uma ação permitida."""
        resolvedor.validar("aberto", "aprovar")

    def test_valida_acao_e_retorna_execucao_validada(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve retornar a execução validada para uma ação permitida."""
        resultado = resolvedor.validar("aberto", "rejeitar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"
        assert resultado.acao.nome == "rejeitar"
        assert resultado.acao.proximo_estado == "rejeitado"
        assert resultado.acao.terminal is True

    def test_deve_lancar_excecao_para_estado_inexistente(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve rejeitar um estado que não existe."""
        with pytest.raises(EstadoInvalidoError) as exc:
            resolvedor.validar("inexistente", "aprovar")

        assert str(exc.value) == (
            "O estado 'inexistente' não existe no arquivo de configuração."
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

    def test_rejeita_proximo_estado_inexistente(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar uma transição para um estado não configurado."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="finalizado",
            terminal=True,
        )
        estados["aberto"] = Estado(
            nome="aberto",
            acoes={"aprovar": acao},
        )
        resolver = DecisaoResolver(estados)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O próximo estado 'finalizado' da ação 'aprovar' "
            "não existe na configuração."
        )

    def test_rejeita_transicao_nao_terminal_para_o_mesmo_estado(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar uma transição não terminal para o estado atual."""
        acao = Acao(
            nome="revisar",
            proximo_estado="aberto",
            terminal=False,
        )
        estados["aberto"] = Estado(
            nome="aberto",
            acoes={"revisar": acao},
        )
        resolver = DecisaoResolver(estados)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "revisar")

        assert (
            str(exc.value) == "A ação 'revisar' do estado 'aberto' "
            "não pode retornar ao mesmo estado."
        )

    def test_permite_transicao_terminal_para_o_mesmo_estado(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve permitir o mesmo estado quando a ação é terminal."""
        acao = Acao(
            nome="encerrar",
            proximo_estado="aberto",
            terminal=True,
        )
        estados["aberto"] = Estado(
            nome="aberto",
            acoes={"encerrar": acao},
        )
        resolver = DecisaoResolver(estados)

        resultado = resolver.validar("aberto", "encerrar")

        assert resultado.acao.terminal is True
        assert resultado.acao.proximo_estado == "aberto"

    @pytest.mark.parametrize(
        ("campo", "valor", "mensagem"),
        [
            (
                "proximo_estado",
                "",
                "O próximo estado da ação 'aprovar' no estado "
                "'aberto' é inválido.",
            ),
            (
                "terminal",
                "sim",
                "O campo 'terminal' da ação 'aprovar' no estado "
                "'aberto' deve ser booleano.",
            ),
        ],
    )
    def test_rejeita_dados_invalidos_da_transicao(
        self,
        estados: dict[str, Estado],
        campo: str,
        valor: object,
        mensagem: str,
    ) -> None:
        """Deve rejeitar dados inválidos na configuração da ação."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=False,
        )

        object.__setattr__(acao, campo, valor)

        estados["aberto"] = Estado(
            nome="aberto",
            acoes={"aprovar": acao},
        )
        resolver = DecisaoResolver(estados)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert str(exc.value) == mensagem


class TestDecisaoResolverInicializacao:
    """Testes da inicialização do resolvedor."""

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
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve aceitar um estado existente na configuração."""
        resultado = resolvedor.validar("aberto", "aprovar")

        assert isinstance(resultado, ExecucaoValidada)
        assert resultado.estado_atual == "aberto"

    @pytest.mark.parametrize(
        "estado_atual",
        ["inexistente", "pendente", "ABERTO"],
    )
    def test_rejeita_estado_inexistente(
        self,
        resolvedor: DecisaoResolver,
        estado_atual: str,
    ) -> None:
        """Deve rejeitar estados que não estejam configurados."""
        with pytest.raises(EstadoInvalidoError) as exc:
            resolvedor.validar(estado_atual, "aprovar")

        assert (
            str(exc.value)
            == f"O estado '{estado_atual}' não existe no arquivo de "
            "configuração."
        )

    def test_valida_estado_antes_da_acao(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve informar o erro de estado antes de validar a ação."""
        with pytest.raises(EstadoInvalidoError) as exc:
            resolvedor.validar("inexistente", "acao_inexistente")

        assert (
            str(exc.value)
            == "O estado 'inexistente' não existe no arquivo de configuração."
        )


class TestDecisaoResolverValidacaoAcao:
    """Testes da disponibilidade de ações."""

    def test_aceita_acao_configurada(
        self,
        resolvedor: DecisaoResolver,
    ) -> None:
        """Deve aceitar uma ação disponível no estado atual."""
        resultado = resolvedor.validar("aberto", "aprovar")

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
        resolvedor: DecisaoResolver,
        nome_acao: str,
    ) -> None:
        """Deve rejeitar ações que não estejam disponíveis."""
        with pytest.raises(AcaoInvalidaError) as exc:
            resolvedor.validar("aberto", nome_acao)

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
        resolvedor: DecisaoResolver,
        estado_atual: str,
    ) -> None:
        """Deve rejeitar ações quando o estado possui acoes=None."""
        with pytest.raises(AcaoInvalidaError) as exc:
            resolvedor.validar(estado_atual, "aprovar")

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


class TestDecisaoResolverValidacaoTransicao:
    """Testes das regras de consistência das transições."""

    def substituir_acao(
        self,
        estados: dict[str, Estado],
        acao: Acao,
        estado_atual: str = "aberto",
    ) -> DecisaoResolver:
        """Substitui uma ação para preparar cenários específicos de teste."""
        estados[estado_atual] = Estado(
            nome=estado_atual,
            acoes={acao.nome: acao},
        )
        return DecisaoResolver(estados)

    def test_rejeita_proximo_estado_vazio(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar um destino vazio."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=True,
        )
        object.__setattr__(acao, "proximo_estado", "")

        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O próximo estado da ação 'aprovar' no estado 'aberto' "
            "é inválido."
        )

    @pytest.mark.parametrize("destino", ["   ", "\t", "\n"])
    def test_rejeita_proximo_estado_com_espacos(
        self,
        estados: dict[str, Estado],
        destino: str,
    ) -> None:
        """Deve rejeitar um destino composto apenas por espaços."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=True,
        )
        object.__setattr__(acao, "proximo_estado", destino)

        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O próximo estado da ação 'aprovar' no estado 'aberto' "
            "é inválido."
        )

    def test_rejeita_proximo_estado_com_tipo_invalido(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar um destino que não seja uma string."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=True,
        )
        object.__setattr__(acao, "proximo_estado", None)

        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O próximo estado da ação 'aprovar' no estado 'aberto' "
            "é inválido."
        )

    def test_rejeita_destino_inexistente(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar uma transição para um estado não configurado."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="finalizado",
            terminal=True,
        )
        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O próximo estado 'finalizado' da ação 'aprovar' "
            "não existe na configuração."
        )

    def test_rejeita_terminal_com_tipo_invalido(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar terminal quando seu valor não for booleano."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=True,
        )
        object.__setattr__(acao, "terminal", "sim")

        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "aprovar")

        assert (
            str(exc.value)
            == "O campo 'terminal' da ação 'aprovar' no estado 'aberto' "
            "deve ser booleano."
        )

    def test_rejeita_transicao_nao_terminal_para_mesmo_estado(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve rejeitar uma transição não terminal para o estado atual."""
        acao = Acao(
            nome="revisar",
            proximo_estado="aberto",
            terminal=False,
        )
        resolver = self.substituir_acao(estados, acao)

        with pytest.raises(AcaoInvalidaError) as exc:
            resolver.validar("aberto", "revisar")

        assert (
            str(exc.value) == "A ação 'revisar' do estado 'aberto' "
            "não pode retornar ao mesmo estado."
        )

    def test_permite_transicao_terminal_para_mesmo_estado(
        self,
        estados: dict[str, Estado],
    ) -> None:
        """Deve permitir destino igual ao estado atual quando terminal."""
        acao = Acao(
            nome="encerrar",
            proximo_estado="aberto",
            terminal=True,
        )
        resolver = self.substituir_acao(estados, acao)

        resultado = resolver.validar("aberto", "encerrar")

        assert resultado.acao.terminal is True
        assert resultado.acao.proximo_estado == "aberto"

    @pytest.mark.parametrize("terminal", [True, False])
    def test_aceita_transicao_para_outro_estado(
        self,
        estados: dict[str, Estado],
        terminal: bool,
    ) -> None:
        """Deve aceitar destino existente diferente do estado atual."""
        acao = Acao(
            nome="aprovar",
            proximo_estado="aprovado",
            terminal=terminal,
        )
        resolver = self.substituir_acao(estados, acao)

        resultado = resolver.validar("aberto", "aprovar")

        assert resultado.acao.proximo_estado == "aprovado"
        assert resultado.acao.terminal is terminal
