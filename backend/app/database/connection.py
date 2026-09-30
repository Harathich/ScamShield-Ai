import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.settings import load_dotenv

# Load env variables
_backend_dir = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=_backend_dir / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

# Default to SQLite if DATABASE_URL is not set or empty
if not DATABASE_URL or not DATABASE_URL.strip():
    DATABASE_URL = f"sqlite:///{_backend_dir}/scamshield.db"

# Create engine with appropriate connect_args for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
    # Test connection if postgresql
    if not DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            pass
except Exception as e:
    print(f"[Warning] Failed to connect to DATABASE_URL ({e}). Falling back to SQLite.")
    sqlite_url = f"sqlite:///{_backend_dir}/scamshield.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
