import sqlite3

DB_PATH = "data/profiles.db"

def save_profile(text, photos, city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO profiles (text, city) VALUES (?, ?)", (text, city))
    profile_id = c.lastrowid
    for file_id in photos:
        c.execute("INSERT INTO photos (profile_id, file_id) VALUES (?, ?)", (profile_id, file_id))
    conn.commit()
    conn.close()
    return profile_id

def get_profiles_by_city(city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, text FROM profiles WHERE city = ?", (city,))
    rows = c.fetchall()
    profiles = []
    for pid, text in rows:
        c.execute("SELECT file_id FROM photos WHERE profile_id = ?", (pid,))
        photos = [row[0] for row in c.fetchall()]
        profiles.append({"id": pid, "text": text, "photos": photos})
    conn.close()
    return profiles
# Future helper functions
