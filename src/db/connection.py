"""Database connection utilities"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

def get_db_url():
    """Get database connection URL from environment variables"""
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER', 'airflow')
    password = os.getenv('POSTGRES_PASSWORD', 'airflow')
    database = os.getenv('POSTGRES_DB', 'airflow')
    
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

def get_engine():
    """Create SQLAlchemy engine"""
    return create_engine(get_db_url())

@contextmanager
def get_session():
    """Context manager for database sessions"""
    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()