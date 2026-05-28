from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./incidents.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_schema():
    """
    Extend existing SQLite tables with new audit timeline columns (idempotent).
    """
    import sqlite3

    conn = sqlite3.connect("./incidents.db")
    cursor = conn.cursor()

    timeline_columns = [
        ("actor", "TEXT DEFAULT 'system'"),
        ("previous_assignee", "TEXT"),
        ("new_assignee", "TEXT"),
        ("escalation_level", "INTEGER"),
        ("event_metadata", "TEXT"),
    ]

    for column_name, column_type in timeline_columns:
        try:
            cursor.execute(
                f"ALTER TABLE timeline_events ADD COLUMN {column_name} {column_type}"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()