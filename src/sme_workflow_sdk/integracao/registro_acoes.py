"""Registro centralizado dos métodos associados às ações do workflow."""

from collections.abc import Callable
from typing import Any

from sme_workflow_sdk.excecoes.integracao import AcaoDuplicadaError

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
        """Remove todas as associações do registro."""
        self._acoes.clear()


registro_acoes = RegistroAcoes()
"""Instância global utilizada para centralizar o registro de ações."""
