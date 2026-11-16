"""Define as exceções base utilizadas pelo SDK de workflow."""


class LeitorWorkflowError(Exception):
    """Exceção base para erros relacionados à leitura da configuração."""


class ValidadorWorkflowError(Exception):
    """Exceção base para erros relacionados à validação da configuração."""


class ValidacaoDominioError(Exception):
    """Exceção base para erros de validação das entidades de domínio."""
