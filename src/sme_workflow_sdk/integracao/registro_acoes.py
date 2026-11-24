"""Registro centralizado dos métodos associados às ações do workflow."""

from collections.abc import Callable
from typing import Any

from sme_workflow_sdk.excecoes.configuracao import (
    AcaoInvalidaError,
    EstadoInvalidoError,
)
from sme_workflow_sdk.excecoes.integracao import AcaoDuplicadaError

# Tipo utilizado para representar os métodos registrados para as ações.
MetodoWorkflow = Callable[..., Any]


class RegistroAcoes:
    """Armazena métodos associados a combinações de estado e ação.

    O registro mantém referências às funções originais, sem criar ou
    armazenar instâncias das classes da aplicação consumidora.

    Cada associação é identificada por uma chave composta pelo estado
    e pela ação. Não permite que métodos diferentes sejam registrados
    para a mesma combinação.
    """

    def __init__(self) -> None:
        """Inicializa um registro vazio de ações."""
        self._acoes: dict[tuple[str, str], MetodoWorkflow] = {}

    def registrar(
        self,
        *,
        estado: str,
        acao: str,
        metodo: MetodoWorkflow,
    ) -> None:
        """Registra um método para uma combinação de estado e ação.

        Se a combinação já estiver registrada pelo mesmo método, a operação
        será considerada idempotente. Caso outro método esteja associado
        à mesma combinação, será lançada uma exceção.

        Args:
            estado (str): Nome do estado ao qual o método será associado.
            acao (str): Nome da ação executada no estado informado.
            metodo (MetodoWorkflow): Referência da função ou método a ser
                registrado.

        Raises:
            AcaoDuplicadaError: Se outro método já estiver registrado
                para a mesma combinação de estado e ação.
        """
        chave = (estado, acao)
        metodo_existente = self._acoes.get(chave)

        if metodo_existente is not None:
            if metodo_existente is metodo:
                return

            raise AcaoDuplicadaError(
                f"Já existe um método registrado para o estado "
                f"'{estado}' e a ação '{acao}': {metodo_existente.__name__}."
            )

        self._acoes[chave] = metodo

    def obter(self, *, estado: str, acao: str) -> MetodoWorkflow | None:
        """Obtém o método associado a uma combinação de estado e ação.

        Args:
            estado (str): Nome do estado utilizado na consulta.
            acao (str): Nome da ação utilizada na consulta.

        Returns:
            MetodoWorkflow | None: O método registrado para a combinação
                informada ou None quando não existir associação.
        """
        return self._acoes.get((estado, acao))

    def listar(self) -> dict[tuple[str, str], MetodoWorkflow]:
        """Retorna uma cópia das ações registradas.

        A cópia permite consultar as associações sem possibilitar alterações
        diretas no dicionário interno do registro.

        Returns:
            dict[tuple[str, str], MetodoWorkflow]: Dicionário contendo as
                combinações de estado e ação e seus respectivos métodos
                registrados.
        """
        return self._acoes.copy()

    def limpar(self) -> None:
        """Remove todas as associações do registro.

        Após a execução, nenhuma combinação de estado e ação permanecerá
        registrada nesta instância.
        """
        self._acoes.clear()

    def validar_declaracoes(self, configuracao: dict[str, Any]) -> None:
        """Verifica se as declarações registradas existem na configuração.

        Percorre as combinações de estado e ação registradas pelos decorators
        e verifica se cada estado existe no YAML e se a ação está declarada
        para esse estado.

        Esta validação deve ser executada durante a inicialização do runtime,
        depois da validação estrutural do YAML e antes da criação do motor.
        Ela valida a compatibilidade das declarações com a configuração, mas
        não executa nem resolve as transições.

        Args:
            configuracao (dict[str, Any]): Configuração do workflow previamente
                carregada e validada pelo configurador.

        Raises:
            EstadoInvalidoError: Se algum estado declarado por um decorator
                não existir na configuração.
            AcaoInvalidaError: Se a ação declarada não estiver disponível
                para o estado correspondente na configuração.
        """
        estados = configuracao["estados"]

        for estado, acao in self._acoes:
            if estado not in estados:
                raise EstadoInvalidoError(
                    f"O estado '{estado}' declarado no decorator não existe "
                    "no arquivo de configuração."
                )

            acoes = estados[estado]["acoes"]
            if acoes is None or acao not in acoes:
                raise AcaoInvalidaError(
                    f"A ação '{acao}' declarada no decorator não está "
                    f"configurada para o estado '{estado}'."
                )


registro_acoes = RegistroAcoes()
"""Instância global utilizada para centralizar o registro de ações."""
