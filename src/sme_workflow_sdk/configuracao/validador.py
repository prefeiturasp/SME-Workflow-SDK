"""Validação da configuração de workflow.

Este módulo expõe :class:`ValidadorWorkflow`, responsável por:

1. Verificar a estrutura da configuração carregada do YAML, garantindo que
   existe um dicionário de ``estados`` não vazio.
2. Validar cada estado individualmente: nome, dados e presença do campo
   ``acoes``.
3. Validar cada ação de cada estado: nome, formato, campos obrigatórios (
   ``proximo_estado``, ``terminal``) e chaves permitidas.
4. Validar as transições entre estados: se o ``proximo_estado`` existe e se é
   coerente com o campo ``terminal``.

O validador **não** lê arquivos — ele trabalha sobre a estrutura
já carregada por :class:`~sme_workflow_sdk.configuracao.leitor.
LeitorWorkflow`. Essa separação permite trocar a origem da
configuração (arquivo, banco, API) sem alterar as regras de
validação.
"""

from typing import Any

from sme_workflow_sdk.excecoes import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)


class ValidadorWorkflow:
    """Responsável por validar a configuração do workflow.

    A classe percorre a configuração em três níveis — estados, ações e
    transições — e lança exceções específicas quando encontra problemas.
    Use-a depois de obter o dicionário do workflow, seja via
    :class:`LeitorWorkflow` ou de outra fonte.

    Examples:
        validador = ValidadorWorkflow()
        validador.validar(configuracao)
    """

    def validar(self, configuracao: dict[str, Any]) -> None:
        """Valida a configuração completa do workflow.

        Verifica, em ordem, se a raiz é um dicionário, se o campo
        ``estados`` é um dicionário não vazio, se cada estado está
        bem formado e, por fim, se as transições entre eles são
        coerentes.

        Args:
            configuracao (dict[str, Any]): Configuração carregada do arquivo
                YAML.

        Raises:
            EstadoInvalidoError:
                - Se a configuração não for um dicionário.
                - Se o campo ``estados`` estiver ausente, não for um
                  dicionário ou estiver vazio.
                - Se algum estado tiver nome ou dados inválidos.
                - Se alguma ação referenciar um estado inexistente.
            AcaoInvalidaError:
                - Se algum estado não possuir o campo ``acoes``.
                - Se ``acoes`` não for dicionário nem ``None``.
                - Se alguma ação estiver mal formada (nome, dados,
                  campos obrigatórios ou chaves extras).
                - Se houver incoerência entre o campo ``terminal``
                  de uma ação e as ações do estado de destino.
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

        Confere se o nome é uma string não vazia, se os dados são um
        dicionário, se o campo ``acoes`` está presente e, quando
        aplicável, delega a validação de cada ação a
        :meth:`_validar_acao`.

        Args:
            nome_estado (str): Nome do estado na configuração.
            dados_estado (Any): Dados associados ao estado.

        Raises:
            EstadoInvalidoError:
                - Se o nome do estado não for uma string não vazia.
                - Se os dados do estado não forem um dicionário.
            AcaoInvalidaError:
                - Se o estado não possuir o campo ``acoes``.
                - Se o campo ``acoes`` não for dicionário nem ``None``.
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

        Confere o nome e o formato dos dados, rejeita chaves que não
        sejam ``proximo_estado`` e ``terminal``, e garante que ambos
        os campos estão presentes e com os tipos esperados.

        Args:
            nome_estado (str): Nome do estado ao qual a ação pertence.
            nome_acao (str): Nome da ação na configuração.
            dados_acao (Any): Dados associados à ação.

        Raises:
            AcaoInvalidaError:
                - Se o nome da ação não for uma string não vazia.
                - Se os dados da ação não forem um dicionário.
                - Se houver chaves além de ``proximo_estado`` e
                  ``terminal``.
                - Se a ação não possuir o campo ``proximo_estado``.
                - Se ``proximo_estado`` não for string não vazia.
                - Se a ação não possuir o campo ``terminal``.
                - Se ``terminal`` não for booleano.
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
                f"A ação '{nome_acao}' do estado '{nome_estado}' possui "
                f"chaves não permitidas: '{", ".join(sorted(chaves_extras))}'"
                f". Permitidas: '{", ".join(sorted(chaves_permitidas))}'."
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
        """Percorre todos os estados e valida cada transição.

        Estados cujo campo ``acoes`` é ``None`` são ignorados, pois
        não possuem transições a validar.

        Args:
            estados (dict[str, Any]): Dicionário de estados da configuração.

        Raises:
            EstadoInvalidoError: Se alguma ação referenciar um estado
                inexistente.
            AcaoInvalidaError: Se houver incoerência entre o campo
                ``terminal`` de alguma ação e as ações do estado de
                destino.
        """
        for nome_estado, dados_estado in estados.items():
            acoes = dados_estado["acoes"]
            if acoes is None:
                continue
            for nome_acao, dados_acao in dados_estado["acoes"].items():
                self._validar_transicao_acao(
                    estados, nome_estado, nome_acao, dados_acao
                )

    def _validar_transicao_acao(
        self,
        estados: dict[str, Any],
        nome_estado: str,
        nome_acao: str,
        dados_acao: dict[str, Any],
    ) -> None:
        """Valida uma única transição de ação.

        Confere se o estado de destino existe e se o campo
        ``terminal`` é coerente com a presença de ações no destino:
        estados terminais devem ir para destinos sem ações; estados
        não terminais devem ir para destinos com ações.

        Args:
            estados (dict[str, Any]): Dicionário completo de estados,
                usado para resolver a referência.
            nome_estado (str): Estado de origem da ação.
            nome_acao (str): Nome da ação que define a transição.
            dados_acao (dict[str, Any]): Dados da ação, já validados
                estruturalmente, contendo ``proximo_estado`` e
                ``terminal``

        Raises:
            EstadoInvalidoError: Se o ``proximo_estado`` não existir na
                configuração.
            AcaoInvalidaError:
                - Se a ação for terminal e o destino possuir ações.
                - Se a ação não for terminal e o destino não possuir
                  ações.
        """
        proximo_estado = dados_acao["proximo_estado"]
        terminal = dados_acao["terminal"]

        if proximo_estado not in estados:
            raise EstadoInvalidoError(
                f"A ação '{nome_acao}' do estado "
                f"'{nome_estado}' referencia o estado "
                f"inexistente '{proximo_estado}'."
            )

        acoes_destino = estados[proximo_estado]["acoes"]
        destino_tem_acoes = acoes_destino is not None

        if terminal and destino_tem_acoes:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado "
                f"'{nome_estado}' é terminal, mas o "
                f"estado de destino '{proximo_estado}' "
                "possui ações configuradas."
            )

        if not terminal and not destino_tem_acoes:
            raise AcaoInvalidaError(
                f"A ação '{nome_acao}' do estado "
                f"'{nome_estado}' não é terminal, mas o "
                f"estado de destino '{proximo_estado}' "
                "não possui ações configuradas."
            )
