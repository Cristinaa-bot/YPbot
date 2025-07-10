import sqlite3

DB_PATH = "data/profiles.db"

def save_profile(text, photo, city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO profiles (text, photo, city) VALUES (?, ?, ?)", (text, photo, city))
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_profiles_by_city(city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, text, photo FROM profiles WHERE city = ?", (city,))
    rows = c.fetchall()
    profiles = [{"id": row[0], "text": row[1], "photo": row[2]} for row in rows]
    conn.close()
    return profiles
