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
    :class:`LeitorWorkflow
    <sme_workflow_sdk.configuracao.leitor.LeitorWorkflow>`
    ou de outra fonte.

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
            EstadoInvalidoError:Lançada quando a configuração apresenta uma
                estrutura inválida, como ausência do campo estados, definição
                inválida ou inexistente de estados, ou quando alguma ação
                referencia um estado que não está definido na configuração.
            AcaoInvalidaError:Lançada quando algum estado não possui o campo
                acoes, quando esse campo apresenta uma definição inválida ou
                está vazio, ou quando alguma ação possui nome ou estrutura
                incorretos, campos obrigatórios ausentes ou propriedades
                adicionais não permitidas. Também é lançada quando há
                incompatibilidade entre o valor do campo terminal de uma ação
                e a existência de ações no estado de destino.
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
            EstadoInvalidoError:Lançada quando o nome do estado não é uma
                string não vazia ou quando sua definição apresenta uma
                estrutura inválida.
            AcaoInvalidaError: Lançada quando o estado não possui o campo
                acoes, quando esse campo não contém uma definição válida ou
                quando apresenta uma definição vazia.
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

        if not isinstance(acoes, dict) or not acoes:
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
            AcaoInvalidaError:Lançada quando o nome da ação não é uma string
                não vazia, quando sua definição apresenta uma estrutura
                inválida ou contém propriedades adicionais além de
                proximo_estado e terminal. Também é lançada quando algum
                desses campos obrigatórios está ausente ou quando
                proximo_estado não é uma string não vazia ou terminal não
                possui um valor booleano.
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
        ``terminal`` é coerente com a configuração de ações do destino.

        Quando ``terminal`` é ``True``, o destino deve possuir
        ``acoes=None``. Quando é ``False``, o destino deve possuir
        um dicionário de ações não vazio.

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
            AcaoInvalidaError:Lançada quando uma ação está definida como
                terminal, mas o estado de destino possui ações disponíveis,
                ou quando uma ação não terminal direciona para um estado que
                não possui ações.
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
