import sqlite3
import uuid
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'aeroguide.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    """Create tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            pnr TEXT,
            age_group TEXT DEFAULT '18-30',
            travel_frequency TEXT DEFAULT 'first_time',
            loyalty_programs TEXT DEFAULT '[]',
            special_assistance TEXT DEFAULT '[]',
            language_preference TEXT DEFAULT 'en',
            dietary_preference TEXT DEFAULT 'both',
            dietary_restrictions TEXT DEFAULT '',
            flight_number TEXT,
            departure_airport TEXT,
            travel_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """)
    conn.commit()
    conn.close()
    print("UserDB initialized at", DB_PATH)

def create_user(profile: dict) -> dict:
    """Create or update a user profile. Returns user_id and session_token."""
    conn = get_db()
    user_id = str(uuid.uuid4())[:8]
    session_token = str(uuid.uuid4())
    expires = datetime.now() + timedelta(hours=24)

    try:
        conn.execute("""
            INSERT INTO users (user_id, full_name, pnr, age_group, travel_frequency,
                loyalty_programs, special_assistance, language_preference,
                dietary_preference, dietary_restrictions, flight_number,
                departure_airport, travel_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            profile.get('full_name', 'Guest'),
            profile.get('pnr', ''),
            profile.get('age_group', '18-30'),
            profile.get('travel_frequency', 'first_time'),
            json.dumps(profile.get('loyalty_programs', [])),
            json.dumps(profile.get('special_assistance', [])),
            profile.get('language_preference', 'en'),
            profile.get('dietary_preference', 'both'),
            profile.get('dietary_restrictions', ''),
            profile.get('flight_number', ''),
            profile.get('departure_airport', ''),
            profile.get('travel_date', ''),
        ))

        conn.execute("""
            INSERT INTO user_sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, session_token, expires.isoformat()))

        conn.commit()
        return {"user_id": user_id, "session_token": session_token}
    except Exception as e:
        print(f"Error creating user: {e}")
        return {"user_id": user_id, "session_token": session_token, "error": str(e)}
    finally:
        conn.close()

def get_user(user_id: str) -> dict:
    """Get user profile by user_id."""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['loyalty_programs'] = json.loads(result.get('loyalty_programs', '[]'))
        result['special_assistance'] = json.loads(result.get('special_assistance', '[]'))
        return result
    return None

def get_user_by_pnr(pnr: str) -> dict:
    """Get user profile by PNR."""
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE pnr = ?", (pnr.upper(),)).fetchone()
    conn.close()
    if row:
        result = dict(row)
        result['loyalty_programs'] = json.loads(result.get('loyalty_programs', '[]'))
        result['special_assistance'] = json.loads(result.get('special_assistance', '[]'))
        return result
    return None

# Initialize on import
init_db()
