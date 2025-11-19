"""
Минимальный набор утилит для работы с PostgreSQL через SQLAlchemy.

Файл отвечает только за инициализацию движков/сессий, а описания моделей вынесены
в shared_utils.database.models.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from shared_utils.database.models import AppDatabaseModel, Base, SoftDeleteMixin, TimestampMixin


@dataclass(slots=True)
class PostgresConfig:
    """
    Small value object that keeps everything required to assemble connection URLs.

    `echo`, `pool_size`, and `max_overflow` expose the knobs we most often tweak
    when tuning SQLAlchemy; defaults match reasonable production values.
    """
    user: str
    password: str
    host: str
    port: int
    database: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_recycle: int = 3600


# ======================================================================================================================
# МЕНЕДЖЕР ДВИЖКОВ И СЕССИЙ
# ======================================================================================================================


class Postgres:
    """
    Lazy singleton that owns both sync and async SQLAlchemy engines/session makers.

    We avoid instantiating state until `initialize` is called, so importing this
    file from unit tests has no side effects.
    """

    _async_engine: Optional[AsyncEngine] = None
    _async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    _sync_engine: Optional[Engine] = None
    _sync_session_factory: Optional[sessionmaker[Session]] = None
    _initialized: bool = False

    @classmethod
    def initialize(cls, config: PostgresConfig) -> None:
        """
        Prepare SQLAlchemy engines and session factories; idempotent by design.

        Args:
            config: connection/query tuning parameters supplied by the caller.
        """
        if cls._initialized:
            return

        async_url = (
            f"postgresql+asyncpg://{config.user}:{config.password}"
            f"@{config.host}:{config.port}/{config.database}"
        )
        sync_url = (
            f"postgresql+psycopg2://{config.user}:{config.password}"
            f"@{config.host}:{config.port}/{config.database}"
        )

        cls._async_engine = create_async_engine(
            async_url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_recycle=config.pool_recycle,
            pool_pre_ping=True,
            future=True,
        )
        cls._async_session_factory = async_sessionmaker(
            cls._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        cls._sync_engine = create_engine(
            sync_url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_recycle=config.pool_recycle,
            pool_pre_ping=True,
            future=True,
        )
        cls._sync_session_factory = sessionmaker(
            cls._sync_engine,
            class_=Session,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

        cls._initialized = True

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Guard helper that keeps the public APIs honest."""
        if not cls._initialized:
            raise RuntimeError("Postgres.initialize must be called before requesting sessions")

    @classmethod
    @asynccontextmanager
    async def get_async_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """
        Async context manager that yields a ready-to-use session instance.

        The helper mirrors the FastAPI dependency pattern:

            async with Postgres.get_async_session() as session:
                await session.execute(...)
        """
        cls._ensure_initialized()
        session = cls._async_session_factory()
        try:
            yield session
        finally:
            await session.close()

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """
        Sync context manager for Celery tasks, CLI tools, or tests.

        Usage mirrors the async variant:

            with Postgres.get_session() as session:
                session.execute(...)
        """
        cls._ensure_initialized()
        session = cls._sync_session_factory()
        try:
            yield session
        finally:
            session.close()


__all__ = [
    "PostgresConfig",
    "Postgres",
    "Base",
    "AppDatabaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
]
