# goodprice-shared-utils — database

Общий пакет с PostgreSQL-утилитами и базовыми SQLAlchemy моделями для сервисов GoodPrice.
Документация из корневого README объединена здесь.

## Подготовка пакета
- Проверьте, что файл `shared-utils/shared_utils/__init__.py` существует (может быть пустой).
- Обновите `version` в `shared-utils/pyproject.toml` до актуальной перед выпуском.
- Опубликуйте код на GitHub и создайте тег/ветку с нужной версией (тег предпочтителен).

## Установка из GitHub
Используйте `pip` с указанием поддиректории:

```bash
pip install "git+https://github.com/<org>/<repo>.git@<tag_or_branch>#egg=goodprice-shared-utils&subdirectory=shared-utils"
```

Пример с тегом `v0.1.0`:

```bash
pip install "git+https://github.com/<org>/<repo>.git@v0.1.0#egg=goodprice-shared-utils&subdirectory=shared-utils"
```

Добавление в `requirements.txt`:

```
git+https://github.com/<org>/<repo>.git@<tag_or_branch>#egg=goodprice-shared-utils&subdirectory=shared-utils
```

Локально из исходников (из каталога `shared-utils`):

```bash
pip install -e .
```

После установки модуль доступен как `shared_utils`.

## Использование

```python
from shared_utils.database import Base, Postgres, PostgresConfig

config = PostgresConfig(
    user="db_user",
    password="db_pass",
    host="postgres",
    port=5432,
    database="goodprice",
)
Postgres.initialize(config)


class Order(Base):
    __tablename__ = "orders"
    ...
```

### Пример моделей с миксинами

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared_utils.database import AppDatabaseModel, SoftDeleteMixin, TimestampMixin


class Customer(TimestampMixin, AppDatabaseModel):
    __tablename__ = "customers"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Product(SoftDeleteMixin, TimestampMixin, AppDatabaseModel):
    __tablename__ = "products"

    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
```

`TimestampMixin` автоматически ведёт `created_at` и `modified_at`, а `SoftDeleteMixin` добавляет флаг `deleted` и гибридные свойства `is_active`/`is_deleted`.

Модели, миксины и менеджер сессий документированы в `shared_utils/database/models.py`
и `shared_utils/database/postgres.py`.
