import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


class Connection:
    def __init__(self):
        self.engine: Engine = create_engine(self._get_db_url())
        self.SessionLocal: sessionmaker[Session] = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def _get_db_url(self) -> str:
        user: str = os.getenv("POSTGRES_USER", "postgres")
        password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
        host: str = os.getenv("POSTGRES_HOST", "localhost")
        port: str = os.getenv("POSTGRES_PORT", "5432")
        db: str = os.getenv("POSTGRES_DB", "ai_news_hub")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    def get_session(self) -> Session:
        return self.SessionLocal()

    def get_session_context(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_engine(self) -> Engine:
        return self.engine


# Create a single instance to be shared across the application
db_connection = Connection()


if __name__ == "__main__":
    import logging

    from app.logging_config import configure_logging

    configure_logging()
    _logger = logging.getLogger(__name__)
    session: Session = db_connection.get_session()
    _logger.info(str(session))
    _logger.info(f"Session type: {type(session)}")
    _logger.info(f"SessionLocal type: {type(db_connection.SessionLocal)}")
    session.close()
