import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()


class Connection:
    def __init__(self):
        self.engine: Engine = create_engine(self.get_database_url())
        self.SessionLocal: sessionmaker[Session] = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_environment(self) -> str:
        return os.getenv("ENVIRONMENT", "LOCAL").upper()

    def get_database_url(self) -> str:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            return database_url

        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "ai_news_aggregator")
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    def get_database_info(self) -> dict:
        url = self.get_database_url()
        env = self.get_environment()

        if (
            "render.com" in url.lower()
            or "amazonaws.com" in url.lower()
            or env == "PRODUCTION"
        ):
            env_type = "PRODUCTION"
        else:
            env_type = "LOCAL"

        masked_url = url
        if "@" in url:
            parts = url.split("@")
            if len(parts) == 2:
                masked_url = f"{parts[0].split('://')[0]}://***@{parts[1]}"

        return {
            "environment": env_type,
            "url_masked": masked_url,
            "host": url.split("@")[-1].split("/")[0] if "@" in url else "localhost",
        }

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
