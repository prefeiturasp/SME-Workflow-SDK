"""Validação da configuração de workflow."""

from typing import Any

from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class ValidadorWorkflow:
    """Responsável por validar a configuração do workflow."""

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração do workflow.

        Args:
            configuracao (dict[str, Any]): Configuração carregada do arquivo
                YAML.

        Raises:
            EstadoInvalidoError: Se a configuração for inválida.
        """
        if not isinstance(configuracao, dict):
            raise EstadoInvalidoError("A configuração fornecida é inválida.")
        estados = configuracao.get("estados")

        if not isinstance(estados, dict) or not estados:
            raise EstadoInvalidoError("Campo 'estados' ausente ou inválido.")

        for nome_estado, dados_estado in estados.items():
            self._validar_estado(nome_estado, dados_estado)

        self._validar_transicoes(estados)

    def _validar_estado(
        self,
        nome_estado: str,
        dados_estado: Any,
    ) -> None:
        """Valida a estrutura de um estado.

        Args:
            nome_estado (str): _description_
            dados_estado (Any): _description_

        Raises:
            AcaoInvalidaError: _description_
            EstadoInvalidoError: _description_
            EstadoInvalidoError: _description_
            EstadoInvalidoError: _description_
        """
        if not isinstance(nome_estado, str) or not nome_estado.strip():
            raise EstadoInvalidoError(
                "O nome de cada estado deve ser uma string não vazia."
            )

        if not isinstance(dados_estado, dict):
            raise EstadoInvalidoError(
                f"Dados do estado '{nome_estado}' inválidos."
            )

        if "acoes" not in dados_estado:
            raise AcaoInvalidaError(
                f"O estado '{nome_estado}' deve possuir o campo 'acoes'."
            )

        acoes = dados_estado["acoes"]
        if acoes is None:
            return

        if not isinstance(acoes, dict):
            raise AcaoInvalidaError(
                f"As ações do estado '{nome_estado}' estão no formato "
                "inválido."
            )

        for nome_acao, dados_acao in acoes.items():
            self._validar_acao(nome_estado, nome_acao, dados_acao)

    def _validar_acao(
        self,
        nome_estado: str,
        nome_acao: str,
        dados_acao: Any,
    ) -> None:
        """Valida a estrutura de uma ação de um estado.

        Verifica se o nome da ação é uma string não vazia, se os dados
        são um dicionário, se os campos 'proximo_estado' e 'terminal'
        estão presentes e se possuem os tipos esperados.

        Args:
            nome_estado (str): Nome do estado ao qual a ação pertence.
            nome_acao (str): Nome da ação na configuração.
            dados_acao (Any): Dados associados à ação.

        Raises:
            AcaoInvalidaError:
                - Se o nome da ação não for uma string não vazia.
                - Se os dados da ação não forem um dicionário.
                - Se a ação não possuir o campo 'proximo_estado'.
                - Se 'proximo_estado' não for uma string não vazia.
                - Se a ação não possuir o campo 'terminal'.
                - Se o campo 'terminal' não for booleano.
        """
        if not isinstance(nome_acao, str) or not nome_acao.strip():
            raise AcaoInvalidaError(
                f"O estado '{nome_estado}' possui uma ação "
                "com nome inválido."
            )

        if not isinstance(dados_acao, dict):
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "está no formato inválido."
            )
        chaves_permitidas = {"proximo_estado", "terminal"}
        chaves_extras = dados_acao.keys() - chaves_permitidas

        if chaves_extras:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                f"possui chaves não permitidas: {", ".join(chaves_extras)}. "
                f"Permitidas: {", ".join(chaves_permitidas)}."
            )

        if "proximo_estado" not in dados_acao:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "deve possuir o campo 'proximo_estado'."
            )

        proximo_estado = dados_acao["proximo_estado"]

        if not isinstance(proximo_estado, str) or not proximo_estado.strip():
            raise AcaoInvalidaError(
                f"O próximo estado da ação '{nome_acao}' "
                f"do estado '{nome_estado}' deve ser uma string "
                "não vazia."
            )

        if "terminal" not in dados_acao:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado '{nome_estado}' "
                "deve possuir o campo 'terminal'."
            )

        if not isinstance(dados_acao["terminal"], bool):
            raise AcaoInvalidaError(
                f"O campo 'terminal' da ação '{nome_acao}' "
                f"do estado '{nome_estado}' deve ser booleano."
            )

    def _validar_transicoes(
        self,
        estados: dict[str, Any],
    ) -> None:
        """Valida referências entre estados e estados terminais.

        Args:
            estados (dict[str, Any]): _description_

        Raises:
            AcaoInvalidaError: _description_
            ConfiguracaoWorkflowInvalidaError: _description_
        """
        for nome_estado, dados_estado in estados.items():
            acoes = dados_estado["acoes"]
            if acoes is None:
                continue
            for nome_acao, dados_acao in dados_estado["acoes"].items():
                proximo_estado = dados_acao["proximo_estado"]
                terminal = dados_acao["terminal"]

                if proximo_estado not in estados:
                    raise EstadoInvalidoError(
                        f"A ação '{nome_acao}' do estado "
                        f"'{nome_estado}' referencia o estado "
                        f"inexistente '{proximo_estado}'."
                    )

                acoes_destino = estados[proximo_estado]["acoes"]

                if terminal and acoes_destino is not None:
                    raise AcaoInvalidaError(
                        f"A ação '{nome_acao}' do estado "
                        f"'{nome_estado}' é terminal, mas o "
                        f"estado de destino '{proximo_estado}' "
                        "possui ações configuradas."
                    )
                if not dados_acao["terminal"] and acoes_destino is None:
                    raise AcaoInvalidaError(
                        f"A ação '{nome_acao}' do estado "
                        f"'{nome_estado}' não é terminal, mas o "
                        f"estado de destino '{proximo_estado}' "
                        "não possui ações configuradas."
                    )
