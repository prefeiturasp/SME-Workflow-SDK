from collections.abc import Callable
from typing import Any, cast

import pytest

from sme_workflow_sdk.excecoes.integracao import (
    AcaoDuplicadaError,
    DeclaracaoWorkflowInvalidaError,
)
from sme_workflow_sdk.integracao import registro_acoes, workflow
from sme_workflow_sdk.integracao.registro_acoes import RegistroAcoes


class TestRegistroAcoes:
    def test_decorator_registra_funcao_original(self) -> None:
        """O decorator registra e preserva a função original."""
        registro = RegistroAcoes()

        def executar_aprovacao(self: object) -> None:
            return None

        registro.registrar(
            estado="pendente", acao="aprovar", metodo=executar_aprovacao
        )

        assert (
            registro.obter(estado="pendente", acao="aprovar")
            is executar_aprovacao
        )

    def test_registro_permite_multiplas_acoes(self) -> None:
        """Permite registrar ações diferentes para o mesmo estado."""
        registro = RegistroAcoes()

        def aprovar() -> str:
            return "aprovado"

        def reprovar() -> str:
            return "reprovado"

        registro.registrar(
            estado="pendente",
            acao="aprovar",
            metodo=aprovar,
        )
        registro.registrar(
            estado="pendente",
            acao="reprovar",
            metodo=reprovar,
        )

        assert (
            registro.obter(
                estado="pendente",
                acao="aprovar",
            )
            is aprovar
        )

        assert (
            registro.obter(
                estado="pendente",
                acao="reprovar",
            )
            is reprovar
        )

    def test_registro_permite_mesma_acao_em_estados_diferentes(self) -> None:
        """A mesma ação pode ser registrada em estados distintos."""
        registro = RegistroAcoes()

        def unidade_executar_aprovacao() -> None:
            return None

        def diretoria_executa_aprovacao() -> None:
            return None

        def administrador_executa_aprovacao() -> None:
            return None

        registro.registrar(
            estado="pendente_unidade",
            acao="aprovar",
            metodo=unidade_executar_aprovacao,
        )
        registro.registrar(
            estado="pendente_diretoria",
            acao="aprovar",
            metodo=diretoria_executa_aprovacao,
        )
        registro.registrar(
            estado="pendente_administrador",
            acao="aprovar",
            metodo=administrador_executa_aprovacao,
        )

        assert (
            registro.obter(estado="pendente_unidade", acao="aprovar")
            is unidade_executar_aprovacao
        )
        assert (
            registro.obter(estado="pendente_diretoria", acao="aprovar")
            is diretoria_executa_aprovacao
        )
        assert (
            registro.obter(estado="pendente_administrador", acao="aprovar")
            is administrador_executa_aprovacao
        )

    def test_registro_rejeita_combinacao_duplicada(self) -> None:
        """Métodos diferentes não podem compartilhar estado e ação."""
        registro = RegistroAcoes()

        def unidade_executar_aprovacao() -> None:
            return None

        def diretoria_executa_aprovacao() -> None:
            return None

        registro.registrar(
            estado="pendente",
            acao="aprovar",
            metodo=unidade_executar_aprovacao,
        )

        with pytest.raises(AcaoDuplicadaError) as exc:
            registro.registrar(
                estado="pendente",
                acao="aprovar",
                metodo=diretoria_executa_aprovacao,
            )
        assert (
            str(exc.value)
            == "Já existe um método registrado para o estado 'pendente' e a "
            "ação 'aprovar': unidade_executar_aprovacao."
        )

    def test_registro_idempotente_para_mesma_funcao(self) -> None:
        """Registrar novamente a mesma função não gera duplicidade."""
        registro = RegistroAcoes()

        def aprovar() -> None:
            return None

        def reprovar() -> None:
            return None

        registro.registrar(estado="pendente", acao="aprovar", metodo=aprovar)
        registro.registrar(estado="pendente", acao="aprovar", metodo=aprovar)
        registro.registrar(estado="pendente", acao="aprovar", metodo=aprovar)

        registro.registrar(estado="pendente", acao="reprovar", metodo=reprovar)
        registro.registrar(estado="pendente", acao="reprovar", metodo=reprovar)
        registro.registrar(estado="pendente", acao="reprovar", metodo=reprovar)

        metodos = registro.listar()
        assert len(metodos) == 2
        assert ("pendente", "aprovar") in metodos
        assert ("pendente", "reprovar") in metodos

    def test_limpar_remove_todos_os_registros(self) -> None:
        """O método limpar remove todas as ações registradas."""
        registro = RegistroAcoes()

        def aprovar() -> None:
            return None

        def reprovar() -> None:
            return None

        registro.registrar(
            estado="pendente",
            acao="aprovar",
            metodo=aprovar,
        )
        registro.registrar(
            estado="pendente",
            acao="reprovar",
            metodo=reprovar,
        )

        registro.limpar()

        assert registro.listar() == {}
        assert (
            registro.obter(
                estado="pendente",
                acao="aprovar",
            )
            is None
        )


class TestDecorators:
    @pytest.mark.parametrize("parametro", ["estado", "acao"])
    @pytest.mark.parametrize("valor", ["", "   ", None, 123])
    def test_decorator_rejeita_parametro_invalido(
        self, parametro: str, valor: Any
    ) -> None:
        """O decorator exige estado e ação como strings não vazias."""
        argumentos = {"estado": "pendente", "acao": "aprovar"}
        argumentos[parametro] = valor

        with pytest.raises(DeclaracaoWorkflowInvalidaError) as exc:
            workflow(**argumentos)

        assert (
            str(exc.value)
            == f"O parâmetro '{parametro}' deve ser uma string não vazia."
        )

    def test_decorator_registra_metodo_na_importacao(self) -> None:
        """A declaração registra apenas os métodos decorados com workflow."""

        registro_acoes.limpar()

        class Servico:
            @workflow(estado="pendente", acao="aprovar")
            def aprovar(self) -> None:
                return None

            @workflow(estado="pendente", acao="reprovar")
            def reprovar(self) -> None:
                return None

            @property
            def obter_dados(self) -> str:
                return "dados"

        assert (
            registro_acoes.obter(estado="pendente", acao="aprovar")
            is Servico.aprovar
        )

        assert (
            registro_acoes.obter(estado="pendente", acao="reprovar")
            is Servico.reprovar
        )

        assert Servico.obter_dados is not None

        registro_acoes.limpar()

    def test_decorator_rejeita_objeto_nao_chamavel(self) -> None:
        """O decorator rejeita objetos que não são métodos ou funções."""

        objeto_invalido = cast(Callable[..., Any], object())

        with pytest.raises(DeclaracaoWorkflowInvalidaError) as exc:
            workflow(estado="pendente", acao="aprovar")(objeto_invalido)
        assert (
            str(exc.value)
            == "O decorator @workflow deve ser aplicado a um método ou função."
        )
