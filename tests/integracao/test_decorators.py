import pytest

from sme_workflow_sdk.excecoes.integracao import AcaoDuplicadaError
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
