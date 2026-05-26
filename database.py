import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We use sqlcipher to ensure DPDP Act compliance for data at rest.
# The URI format is sqlite+pysqlcipher://:passphrase@/file_path
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./hospital.db")
SQLCIPHER_PASSPHRASE = os.getenv("SQLCIPHER_PASSPHRASE", "default_secret_passphrase")

# If you run into driver issues on Windows with pysqlcipher, 
# you can temporarily fallback to standard sqlite by using:
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"
SQLALCHEMY_DATABASE_URL = f"sqlite+pysqlcipher://:{SQLCIPHER_PASSPHRASE}@/{SQLITE_DB_PATH}"

# Note: check_same_thread=False is needed for SQLite in FastAPI if not using async engine
try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
except Exception as e:
    # Fallback to standard sqlite if sqlcipher is not installed locally
    print(f"Warning: Falling back to unencrypted SQLite due to: {e}")
    engine = create_engine(
        f"sqlite:///{SQLITE_DB_PATH}", connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
