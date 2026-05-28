
import sys
import os

from app.database.models import BaseSchema
from app.database.connection import db_connection

def create_tables():
    BaseSchema.metadata.create_all(db_connection.get_engine())

def drop_tables():
    BaseSchema.metadata.drop_all(db_connection.engine)   
    
if __name__ == "__main__":
    drop_tables()
    create_tables()
