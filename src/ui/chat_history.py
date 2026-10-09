"""SQLite persistence for chat sessions and messages."""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "chat_history.db"


def _connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                sources_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        connection.execute("PRAGMA foreign_keys = ON")


def create_session(session_id: str, title: str):
    with _connect() as connection:
        connection.execute(
            "INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title)
        )


def list_sessions():
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id, title FROM sessions ORDER BY updated_at DESC, created_at DESC"
        ).fetchall()
        return {row["id"]: {"title": row["title"]} for row in rows}


def get_messages(session_id: str):
    with _connect() as connection:
        rows = connection.execute(
            "SELECT role, content, sources_json FROM messages "
            "WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        return [
            {"role": row["role"], "content": row["content"],
             "sources": json.loads(row["sources_json"])}
            for row in rows
        ]


def add_message(session_id: str, role: str, content: str, sources=None):
    sources_json = json.dumps(sources or [], ensure_ascii=False)
    with _connect() as connection:
        connection.execute(
            "INSERT INTO messages (session_id, role, content, sources_json) "
            "VALUES (?, ?, ?, ?)",
            (session_id, role, content, sources_json),
        )
        connection.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,),
        )


def update_title(session_id: str, title: str):
    with _connect() as connection:
        connection.execute(
            "UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, session_id),
        )


def delete_session(session_id: str):
    with _connect() as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
