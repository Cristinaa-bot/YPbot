import sqlite3

DB_PATH = "data/profiles.db"

async def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            photo TEXT,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()
