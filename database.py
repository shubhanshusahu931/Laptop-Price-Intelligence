# database.py — Updated with User Auth Support
import sqlite3, os, hashlib, secrets

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Existing laptops table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS laptop_results (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT,
            price           INTEGER,
            link            TEXT UNIQUE,
            platform        TEXT,
            image           TEXT,
            ram             INTEGER,
            ram_type        TEXT,
            storage         INTEGER,
            storage_type    TEXT,
            rating          TEXT,
            specs_summary   TEXT,
            predicted_price INTEGER,
            user_id         INTEGER DEFAULT NULL,
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT UNIQUE NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            password_hash   TEXT NOT NULL,
            avatar_color    TEXT DEFAULT '#f5a623',
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login      DATETIME
        )
    """)
    
    # Sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token           TEXT PRIMARY KEY,
            user_id         INTEGER NOT NULL,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at      DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # User wishlists (server-side)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT,
            price       INTEGER,
            link        TEXT,
            image       TEXT,
            platform    TEXT,
            specs       TEXT,
            added_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password, stored_hash):
    try:
        salt, hashed = stored_hash.split(":")
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except:
        return False

def create_session(user_id):
    token = secrets.token_urlsafe(32)
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO sessions (token, user_id, expires_at)
        VALUES (?, ?, datetime('now', '+7 days'))
    """, (token, user_id))
    conn.commit()
    conn.close()
    return token

def get_user_by_token(token):
    if not token:
        return None
    conn = get_db_connection()
    row = conn.execute("""
        SELECT u.* FROM users u
        JOIN sessions s ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    """, (token,)).fetchone()
    conn.close()
    return row

def delete_session(token):
    conn = get_db_connection()
    conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()
