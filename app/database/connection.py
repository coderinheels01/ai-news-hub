import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session


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
    session: Session = db_connection.get_session()
    print(session)
    print(f"Session type: {type(session)}")
    print(f"SessionLocal type: {type(db_connection.SessionLocal)}")
    session.close()  # Don't forget to close the session


