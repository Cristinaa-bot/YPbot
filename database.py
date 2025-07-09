import sqlite3

def init_db():
    conn = sqlite3.connect("data/bot.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        city TEXT,
        nationality TEXT,
        dates TEXT,
        availability TEXT,
        preferences TEXT,
        whatsapp TEXT,
        photos TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        user_id INTEGER,
        profile_id INTEGER,
        category TEXT,
        PRIMARY KEY (user_id, profile_id, category)
    )
    """)

    conn.commit()
    conn.close()
