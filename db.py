
# db.py (Database Helper)

import sqlite3

def init_db():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_file(filename, filepath):
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("INSERT INTO uploaded_files (filename, filepath) VALUES (?, ?)", (filename, filepath))
    conn.commit()
    conn.close()

def get_files():
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT id, filename FROM uploaded_files")
    files = c.fetchall()
    conn.close()
    return files

def delete_file(file_id):
    conn = sqlite3.connect("files.db")
    c = conn.cursor()
    c.execute("SELECT filepath FROM uploaded_files WHERE id = ?", (file_id,))
    filepath = c.fetchone()
    if filepath:
        c.execute("DELETE FROM uploaded_files WHERE id = ?", (file_id,))
        conn.commit()
    conn.close()
    return filepath[0] if filepath else None
