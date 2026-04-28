from __future__ import annotations


class DataSourceError(RuntimeError):
    """Erro base para falhas em fontes de dados externas."""


class DataUnavailableError(DataSourceError):
    """Fonte externa indisponivel, ausente ou sem resposta utilizavel."""


class DataParsingError(DataSourceError):
    """Resposta recebida, mas em formato invalido ou inesperado."""


class DataValidationError(DataSourceError):
    """Dados recebidos nao passaram em validacoes de negocio ou schema."""
