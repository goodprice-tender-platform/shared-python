"""
Корневой пакет общих утилит GoodPrice.

Экспортирует наиболее часто используемые сущности, чтобы сервисам было удобно
делать `from shared_utils import Postgres, Base`.
"""

from .database.models import AppDatabaseModel, Base, SoftDeleteMixin, TimestampMixin
from .database.postgres import Postgres, PostgresConfig

__all__ = [
    "Base",
    "AppDatabaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "Postgres",
    "PostgresConfig",
]

