import sqlite3

DB_NAME = "ims.db"


def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_columns(cursor, table, columns):
    cursor.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cursor.fetchall()}

    for name, definition in columns.items():
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        type TEXT,
        severity TEXT,
        service TEXT,
        metric TEXT,
        value TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS incidents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id INTEGER,
        title TEXT,
        description TEXT,
        alert_type TEXT,
        severity TEXT,
        priority TEXT,
        status TEXT,
        service TEXT,
        assignee TEXT,
        workflow_path TEXT,
        notification_channel TEXT,
        escalation_level INTEGER DEFAULT 0,
        sla_minutes INTEGER DEFAULT 60,
        remediation_action TEXT,
        acknowledged_at TEXT,
        resolved_at TEXT,
        resolution_notes TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS timeline_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER,
        stage TEXT,
        event_type TEXT,
        description TEXT,
        actor TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id INTEGER,
        channel TEXT,
        recipient TEXT,
        status TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    _ensure_columns(c, "alerts", {
        "service": "TEXT",
        "metric": "TEXT",
        "value": "TEXT",
    })

    _ensure_columns(c, "incidents", {
        "description": "TEXT",
        "service": "TEXT",
        "notification_channel": "TEXT",
        "escalation_level": "INTEGER DEFAULT 0",
        "sla_minutes": "INTEGER DEFAULT 60",
        "remediation_action": "TEXT",
        "acknowledged_at": "TEXT",
        "resolved_at": "TEXT",
        "resolution_notes": "TEXT",
    })

    conn.commit()
    conn.close()
