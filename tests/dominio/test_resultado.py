from datetime import UTC, datetime, timedelta
from typing import cast

import pytest

from sme_workflow_sdk import ContextoExecucao, ResultadoWorkflow
from sme_workflow_sdk.excecoes.base import ValidacaoDominioError


class TestResultadoWorkflow:
    """Criação e validação do resultado de execução."""

    def test_cria_resultado_valido(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve criar resultado quando todos os campos são válidos."""
        resultado = ResultadoWorkflow(
            identificador=cast(str, dados_resultado["identificador"]),
            estado_anterior=cast(str, dados_resultado["estado_anterior"]),
            acao=cast(str, dados_resultado["acao"]),
            proximo_estado=cast(str, dados_resultado["proximo_estado"]),
            terminal=cast(bool, dados_resultado["terminal"]),
            sucesso=cast(bool, dados_resultado["sucesso"]),
            mensagem=cast(str, dados_resultado["mensagem"]),
            inicio=cast(datetime, dados_resultado["inicio"]),
            fim=cast(datetime, dados_resultado["fim"]),
            autor=cast(str, dados_resultado["autor"]),
            contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
        )

        assert resultado.identificador == "execucao-123"
        assert resultado.estado_anterior == "aberto"
        assert resultado.acao == "aprovar"
        assert resultado.proximo_estado == "aprovado"
        assert resultado.terminal is True
        assert resultado.sucesso is True
        assert resultado.mensagem == "Solicitação aprovada com sucesso."
        assert resultado.fim >= resultado.inicio
        assert resultado.autor == "usuario_1"

    def test_aceita_resultado_malsucedido_sem_mudar_estado(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve aceitar falha que mantém o estado anterior."""
        dados_resultado.update(
            sucesso=False,
            mensagem="Não foi possível aprovar a solicitação.",
            proximo_estado="aberto",
            terminal=False,
        )

        resultado = ResultadoWorkflow(
            identificador=cast(str, dados_resultado["identificador"]),
            estado_anterior=cast(str, dados_resultado["estado_anterior"]),
            acao=cast(str, dados_resultado["acao"]),
            proximo_estado=cast(str, dados_resultado["proximo_estado"]),
            terminal=cast(bool, dados_resultado["terminal"]),
            sucesso=cast(bool, dados_resultado["sucesso"]),
            mensagem=cast(str, dados_resultado["mensagem"]),
            inicio=cast(datetime, dados_resultado["inicio"]),
            fim=cast(datetime, dados_resultado["fim"]),
            autor=cast(str, dados_resultado["autor"]),
            contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
        )

        assert resultado.sucesso is False
        assert resultado.proximo_estado == resultado.estado_anterior
        assert resultado.mensagem == "Não foi possível aprovar a solicitação."

    @pytest.mark.parametrize(
        ("campo", "valor", "mensagem"),
        [
            (
                "identificador",
                "",
                "ResultadoWorkflow.identificador não pode ser vazio",
            ),
            (
                "estado_anterior",
                "",
                "ResultadoWorkflow.estado_anterior não pode ser vazio",
            ),
            ("acao", "", "ResultadoWorkflow.acao não pode ser vazio"),
            (
                "proximo_estado",
                "",
                "ResultadoWorkflow.proximo_estado não pode ser vazio",
            ),
            ("autor", "", "ResultadoWorkflow.autor não pode ser vazio"),
            ("mensagem", "", "ResultadoWorkflow.mensagem não pode ser vazio"),
        ],
    )
    def test_rejeita_strings_obrigatorias_vazias(
        self,
        dados_resultado: dict[str, object],
        campo: str,
        valor: str,
        mensagem: str,
    ) -> None:
        """Deve rejeitar campos textuais vazios."""
        dados_resultado[campo] = valor

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert str(exc.value) == mensagem

    @pytest.mark.parametrize(
        ("campo", "valor", "mensagem"),
        [
            (
                "terminal",
                1,
                "ResultadoWorkflow.terminal deve ser bool, recebido int",
            ),
            (
                "sucesso",
                "sim",
                "ResultadoWorkflow.sucesso deve ser bool, recebido str",
            ),
        ],
    )
    def test_rejeita_booleanos_invalidos(
        self,
        dados_resultado: dict[str, object],
        campo: str,
        valor: object,
        mensagem: str,
    ) -> None:
        """Deve rejeitar campos booleanos com tipo inválido."""
        dados_resultado[campo] = valor

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert str(exc.value) == mensagem

    def test_rejeita_inicio_com_tipo_invalido(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar início que não seja datetime."""
        dados_resultado["inicio"] = "2026-01-01"

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert (
            str(exc.value)
            == "ResultadoWorkflow.inicio deve ser datetime, recebido str"
        )

    def test_rejeita_contexto_com_tipo_invalido(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar contexto que não seja ContextoExecucao."""
        dados_resultado["contexto"] = {}

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert (
            str(exc.value) == "ResultadoWorkflow.contexto deve ser "
            "ContextoExecucao, recebido dict"
        )

    def test_rejeita_fim_anterior_ao_inicio(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar resultado finalizado antes do início."""
        inicio = dados_resultado["inicio"]
        assert isinstance(inicio, datetime)
        dados_resultado["fim"] = inicio - timedelta(seconds=1)

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert (
            str(exc.value)
            == "ResultadoWorkflow.fim não pode ser anterior a inicio"
        )

    def test_rejeita_fusos_horarios_incompativeis(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar comparação entre datetime sem fuso e com fuso."""
        dados_resultado["inicio"] = datetime(2026, 1, 1, 10, 0)
        dados_resultado["fim"] = datetime(2026, 1, 1, 10, 1, tzinfo=UTC)

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert (
            str(exc.value)
            == "ResultadoWorkflow.inicio e fim devem ter fusos horários "
            "compatíveis"
        )

    def test_rejeita_transicao_bem_sucedida_nao_terminal_para_mesmo_estado(
        self, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar sucesso não terminal que mantém o mesmo estado."""
        dados_resultado.update(
            sucesso=True,
            terminal=False,
            estado_anterior="aberto",
            proximo_estado="aberto",
        )

        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )

        assert (
            str(exc.value)
            == "Ação aprovar em aberto aponta para aberto. Uma execução "
            "bem-sucedida e não terminal deve indicar um estado de destino "
            "diferente do estado anterior."
        )

    def test_rejeita_estado_anterior_invalido(
        self, valor_invalido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar estado_anterior fora da regra."""
        with pytest.raises(
            ValidacaoDominioError,
        ) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=valor_invalido,
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )
        assert (
            f"ResultadoWorkflow.estado_anterior inválido ('{valor_invalido}')."
            " O valor deve conter apenas letras e sublinhados ('_') entre "
            "palavras (ex.: 'em_execucao'). Não são permitidos sublinhados no "
            "início, no fim ou duplicados." in str(exc.value)
        )

    def test_aceita_estado_anterior_valido(
        self, valor_valido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve aceitar estado_anterior como válido."""

        resultado = ResultadoWorkflow(
            identificador=cast(str, dados_resultado["identificador"]),
            estado_anterior=valor_valido,
            acao=cast(str, dados_resultado["acao"]),
            proximo_estado=cast(str, dados_resultado["proximo_estado"]),
            terminal=cast(bool, dados_resultado["terminal"]),
            sucesso=cast(bool, dados_resultado["sucesso"]),
            mensagem=cast(str, dados_resultado["mensagem"]),
            inicio=cast(datetime, dados_resultado["inicio"]),
            fim=cast(datetime, dados_resultado["fim"]),
            autor=cast(str, dados_resultado["autor"]),
            contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
        )
        assert resultado.estado_anterior == valor_valido

    def test_rejeita_acao_invalida(
        self, valor_invalido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar acao fora da regra."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=valor_invalido,
                proximo_estado=cast(str, dados_resultado["proximo_estado"]),
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )
        assert (
            f"ResultadoWorkflow.acao inválido ('{valor_invalido}'). O valor "
            "deve conter apenas letras e sublinhados ('_') entre palavras "
            "(ex.: 'em_execucao'). Não são permitidos sublinhados no início, "
            "no fim ou duplicados." in str(exc.value)
        )

    def test_aceita_acao_valida(
        self, valor_valido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve aceitar acao como válida."""

        resultado = ResultadoWorkflow(
            identificador=cast(str, dados_resultado["identificador"]),
            estado_anterior=cast(str, dados_resultado["estado_anterior"]),
            acao=valor_valido,
            proximo_estado=cast(str, dados_resultado["proximo_estado"]),
            terminal=cast(bool, dados_resultado["terminal"]),
            sucesso=cast(bool, dados_resultado["sucesso"]),
            mensagem=cast(str, dados_resultado["mensagem"]),
            inicio=cast(datetime, dados_resultado["inicio"]),
            fim=cast(datetime, dados_resultado["fim"]),
            autor=cast(str, dados_resultado["autor"]),
            contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
        )
        assert resultado.acao == valor_valido

    def test_rejeita_proximo_estado_invalido(
        self, valor_invalido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve rejeitar proximo_estado fora da regra."""
        with pytest.raises(ValidacaoDominioError) as exc:
            ResultadoWorkflow(
                identificador=cast(str, dados_resultado["identificador"]),
                estado_anterior=cast(str, dados_resultado["estado_anterior"]),
                acao=cast(str, dados_resultado["acao"]),
                proximo_estado=valor_invalido,
                terminal=cast(bool, dados_resultado["terminal"]),
                sucesso=cast(bool, dados_resultado["sucesso"]),
                mensagem=cast(str, dados_resultado["mensagem"]),
                inicio=cast(datetime, dados_resultado["inicio"]),
                fim=cast(datetime, dados_resultado["fim"]),
                autor=cast(str, dados_resultado["autor"]),
                contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
            )
        assert (
            f"ResultadoWorkflow.proximo_estado inválido ('{valor_invalido}'). "
            "O valor deve conter apenas letras e sublinhados ('_') entre "
            "palavras (ex.: 'em_execucao'). Não são permitidos sublinhados no "
            "início, no fim ou duplicados." in str(exc.value)
        )

    def test_aceita_proximo_estado_valido(
        self, valor_valido: str, dados_resultado: dict[str, object]
    ) -> None:
        """Deve aceitar proximo_estado como válido."""

        resultado = ResultadoWorkflow(
            identificador=cast(str, dados_resultado["identificador"]),
            estado_anterior=cast(str, dados_resultado["estado_anterior"]),
            acao=cast(str, dados_resultado["acao"]),
            proximo_estado=valor_valido,
            terminal=cast(bool, dados_resultado["terminal"]),
            sucesso=cast(bool, dados_resultado["sucesso"]),
            mensagem=cast(str, dados_resultado["mensagem"]),
            inicio=cast(datetime, dados_resultado["inicio"]),
            fim=cast(datetime, dados_resultado["fim"]),
            autor=cast(str, dados_resultado["autor"]),
            contexto=cast(ContextoExecucao, dados_resultado["contexto"]),
        )
        assert resultado.proximo_estado == valor_valido
