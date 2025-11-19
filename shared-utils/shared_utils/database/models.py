"""
Базовые модели и миксины для SQLAlchemy.

Вынесено в отдельный модуль, чтобы postgres.py занимался только инфраструктурой
инициализации, а доменные сущности — наследовались отсюда.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, MetaData, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ======================================================================================================================
# METADATA И БАЗА
# ======================================================================================================================

metadata = MetaData()


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    metadata = metadata
    __abstract__ = True


# ======================================================================================================================
# МИКСИНЫ
# ======================================================================================================================

class TimestampMixin:
    """
    Миксин для автоматического управления временными метками.
    Аналог Tortoise: created_at (auto_now_add), modified_at (auto_now)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=func.now(),
        nullable=False,
        comment="Дата создания",
    )

    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата последнего изменения",
    )


class SoftDeleteMixin:
    """
    Миксин для soft delete (помечает запись как удаленную вместо физического удаления).
    Аналог Tortoise: FakeDeleted + FakeDeletedQuerySet
    """

    deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Помечено как удаленное (soft delete)",
    )

    @hybrid_property
    def is_active(self) -> bool:
        """Проверка, что запись активна (не удалена)."""

        return not self.deleted

    @hybrid_property
    def is_deleted(self) -> bool:
        """Проверка, что запись удалена."""

        return self.deleted


# ======================================================================================================================
# БАЗОВАЯ МОДЕЛЬ
# ======================================================================================================================

class AppDatabaseModel(Base):
    """
    Базовая модель для всех сущностей в системе.
    Заменяет Tortoise: AppDatabaseModel (BaseModel)
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор",
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Автоматическое определение имени таблицы из имени класса (lowercase)."""

        return cls.__name__.lower()

    def to_dict(
        self,
        exclude: Optional[List[str]] = None,
        include_relations: bool = False,
        exclude_none: bool = False,
    ) -> Dict[str, Any]:
        """
        Сериализация модели в словарь.
        Аналог Tortoise: values_dict()
        """

        exclude = exclude or []
        result: Dict[str, Any] = {}

        for column in self.__table__.columns:
            if column.name in exclude:
                continue

            value = getattr(self, column.name, None)
            if exclude_none and value is None:
                continue

            if isinstance(value, datetime):
                value = value.isoformat()

            result[column.name] = value

        # TODO: добавить поддержку relationships если include_relations=True
        return result

    def __repr__(self) -> str:
        """Строковое представление модели."""

        return f"<{self.__class__.__name__}(id={self.id})>"


__all__ = [
    "Base",
    "AppDatabaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "metadata",
]

