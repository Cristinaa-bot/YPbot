import sqlite3

DB_PATH = "data/profiles.db"

async def create_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            city TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()
