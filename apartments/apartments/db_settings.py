from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.engine import Engine

from apartments import settings
from .models import Base


def db_connect() -> Engine:
    return create_engine(URL.create(**settings.DATABASE))


def create_items_table(engine: Engine):
    Base.metadata.create_all(engine)