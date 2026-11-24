from collections.abc import Callable
from inspect import unwrap
from pathlib import Path
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from sme_workflow_sdk.excecoes.configuracao import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)
from sme_workflow_sdk.excecoes.integracao import (
    AcaoDuplicadaError,
    DeclaracaoWorkflowInvalidaError,
    EstadoWorkflowIncompativelError,
)
from sme_workflow_sdk.integracao import registro_acoes, workflow
from sme_workflow_sdk.integracao.registro_acoes import RegistroAcoes
from sme_workflow_sdk.runtime import configure, shutdown


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

    def test_listar_retorna_copia_dos_registros(self) -> None:
        """Alterações na cópia não modificam o registro original."""
        registro = RegistroAcoes()

        def aprovar() -> None:
            return None

        registro.registrar(
            estado="pendente",
            acao="aprovar",
            metodo=aprovar,
        )

        registros = registro.listar()
        registros.clear()

        assert (
            registro.obter(
                estado="pendente",
                acao="aprovar",
            )
            is aprovar
        )

    def test_aceita_declaracao_existente_na_configuracao(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Não lança exceção quando estado e ação existem no YAML."""
        registro = RegistroAcoes()

        def aprovar() -> None:
            return None

        registro.registrar(
            estado="aberto",
            acao="aprovar",
            metodo=aprovar,
        )

        registro.validar_declaracoes(workflow_exemplo_dict)

    def test_rejeita_estado_ausente_na_configuracao(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Rejeita estado declarado no decorator que não existe no YAML."""
        registro = RegistroAcoes()

        def aprovar() -> None:
            return None

        registro.registrar(
            estado="inexistente",
            acao="aprovar",
            metodo=aprovar,
        )

        with pytest.raises(EstadoInvalidoError) as exc:
            registro.validar_declaracoes(workflow_exemplo_dict)

        assert str(exc.value) == (
            "O estado 'inexistente' declarado no decorator não existe "
            "no arquivo de configuração."
        )

    def test_rejeita_acao_ausente_no_estado(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Rejeita ação que não está declarada para o estado no YAML."""
        registro = RegistroAcoes()

        def cancelar() -> None:
            return None

        registro.registrar(
            estado="aberto",
            acao="cancelar",
            metodo=cancelar,
        )

        with pytest.raises(AcaoInvalidaError) as exc:
            registro.validar_declaracoes(workflow_exemplo_dict)

        assert str(exc.value) == (
            "A ação 'cancelar' declarada no decorator não está "
            "configurada para o estado 'aberto'."
        )

    def test_rejeita_acao_em_estado_sem_acoes(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Rejeita ação declarada para um estado terminal sem ações."""
        registro = RegistroAcoes()

        def reabrir() -> None:
            return None

        registro.registrar(
            estado="concluido",
            acao="reabrir",
            metodo=reabrir,
        )

        with pytest.raises(AcaoInvalidaError) as exc:
            registro.validar_declaracoes(workflow_exemplo_dict)

        assert str(exc.value) == (
            "A ação 'reabrir' declarada no decorator não está "
            "configurada para o estado 'concluido'."
        )

    def test_aceita_registro_vazio(
        self,
        workflow_exemplo_dict: dict[str, Any],
    ) -> None:
        """Não exige declarações quando nenhum método foi registrado."""
        registro = RegistroAcoes()

        registro.validar_declaracoes(workflow_exemplo_dict)


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

        class Servico:
            @workflow(estado="pendente", acao="aprovar")
            def aprovar(self) -> None:
                return None

            @workflow(estado="pendente", acao="reprovar")
            def reprovar(self) -> None:
                return None

            def obter_dados(self) -> str:
                return "dados"

        assert registro_acoes.obter(
            estado="pendente", acao="aprovar"
        ) is unwrap(Servico.aprovar)

        assert registro_acoes.obter(
            estado="pendente", acao="reprovar"
        ) is unwrap(Servico.reprovar)

        assert (
            registro_acoes.obter(
                estado="pendente",
                acao="obter_dados",
            )
            is None
        )

    def test_decorator_rejeita_objeto_nao_chamavel(self) -> None:
        """O decorator rejeita objetos que não são métodos ou funções."""

        objeto_invalido = cast(Callable[..., Any], object())

        with pytest.raises(DeclaracaoWorkflowInvalidaError) as exc:
            workflow(estado="pendente", acao="aprovar")(objeto_invalido)
        assert (
            str(exc.value)
            == "O decorator @workflow deve ser aplicado a um método ou função."
        )

    def test_decorator_preserva_funcionamento_do_metodo(self) -> None:
        """O método decorado mantém seus argumentos e retorno."""

        class Servico:
            @workflow(estado="pendente", acao="aprovar")
            def aprovar(self, valor: int) -> int:
                return valor * 2

        servico = Servico()

        motor = Mock()
        with patch(
            "sme_workflow_sdk.runtime.get_workflow",
            return_value=motor,
        ):
            resultado = servico.aprovar(
                estado="pendente",
                valor=10,
            )

        assert resultado == 20

    @pytest.mark.parametrize(
        ("estado", "acao"),
        [
            ("", "aprovar"),
            ("   ", "aprovar"),
            (None, "aprovar"),
            (123, "aprovar"),
            ("pendente", ""),
            ("pendente", "   "),
            ("pendente", None),
            ("pendente", 123),
        ],
    )
    def test_decorator_rejeita_estado_ou_acao_invalido(
        self,
        estado: object,
        acao: object,
    ) -> None:
        """O decorator exige estado e ação como strings não vazias."""
        workflow_generico = cast(
            Callable[..., object],
            workflow,
        )

        with pytest.raises(DeclaracaoWorkflowInvalidaError) as exc:
            workflow_generico(
                estado=estado,
                acao=acao,
            )
        assert "deve ser uma string não vazia." in str(exc.value)

    def test_decorator_rejeita_estado_diferente_do_declarado(
        self,
        yaml_valido: Path,
    ) -> None:
        """Rejeita estado diferente daquele declarado no decorator."""
        configure(yaml_valido)
        chamadas: list[int] = []

        class Servico:
            @workflow(estado="aberto", acao="aprovar")
            def aprovar(self, valor: int) -> int:
                chamadas.append(valor)
                return valor * 2

        with pytest.raises(EstadoWorkflowIncompativelError) as exc:
            Servico().aprovar(estado="aprovado", valor=10)

        assert (
            str(exc.value)
            == "A ação 'aprovar' foi declarada para o estado 'aberto', mas "
            "recebeu o estado 'aprovado'."
        )
        assert chamadas == []

    def test_decorator_exige_estado_na_chamada(
        self,
        yaml_valido: Path,
    ) -> None:
        """Exige o parâmetro estado ao chamar um método decorado."""
        configure(yaml_valido)

        class Servico:
            @workflow(estado="aberto", acao="aprovar")
            def aprovar(self, valor: int) -> int:
                return valor * 2

        with pytest.raises(TypeError) as exc:
            Servico().aprovar(valor=10)

        assert "missing 1 required keyword-only argument: 'estado'" in str(
            exc.value
        )

    def test_decorator_nao_depende_runtime_configurado(self) -> None:
        """Executa o método decorado sem depender do runtime"""

        shutdown()

        class Servico:
            @workflow(estado="aberto", acao="aprovar")
            def aprovar(self, valor: int) -> int:
                return valor * 2

        resultado = Servico().aprovar(
            estado="aberto",
            valor=10,
        )

        assert resultado == 20

    def test_decorator_rejeita_metodos_com_mesma_combinacao(self) -> None:
        """Não permite métodos diferentes para a mesma combinação."""

        class Servico:
            @workflow(estado="pendente", acao="aprovar")
            def aprovar(self) -> None:
                return None

        with pytest.raises(AcaoDuplicadaError) as exc:

            class OutroServico:
                @workflow(estado="pendente", acao="aprovar")
                def aprovar(self) -> None:
                    return None

        assert (
            str(exc.value)
            == "Já existe um método registrado para o estado 'pendente' e a "
            "ação 'aprovar': aprovar."
        )
