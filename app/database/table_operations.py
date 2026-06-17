import logging

from app.database.connection import db_connection
from app.database.models import BaseSchema

logger = logging.getLogger(__name__)


def create_tables():
    BaseSchema.metadata.create_all(db_connection.get_engine())


def drop_tables(table_name: str):
    table = BaseSchema.metadata.tables.get(table_name)
    if table is not None:
        table.drop(db_connection.get_engine())
    else:
        logger.warning(f"Table '{table_name}' not found")


if __name__ == "__main__":
    drop_tables("digest")
    drop_tables("digest")

    create_tables()
