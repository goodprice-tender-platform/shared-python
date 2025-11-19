# goodprice-shared-utils

Общий пакет с PostgreSQL-утилитами и базовыми SQLAlchemy моделями для сервисов GoodPrice.

## Установка

Из гита (например, через тег релиза):

```bash
pip install "git+ssh://git@your-git.example.com/goodprice/shared-utils.git@v0.1.0#egg=goodprice-shared-utils"
```

Локально из исходников:

```bash
pip install -e .
```

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

Модели, миксины и менеджер сессий документированы в `shared_utils/database/models.py`
и `shared_utils/database/postgres.py`.

