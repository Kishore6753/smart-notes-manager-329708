#!/usr/bin/env python3
"""
Initialize the SQLite schema for the Smart Notes Manager application.

This script is intentionally idempotent: it uses CREATE TABLE IF NOT EXISTS and
CREATE INDEX IF NOT EXISTS so it can be re-run safely.

Contract:
- Inputs: None (uses local `myapp.db` in the current working directory).
- Outputs: Creates/updates tables and indexes.
- Errors: Raises sqlite3.Error on DB failures.
- Side effects: Writes schema to `myapp.db`.
"""

from __future__ import annotations

import sqlite3

DB_NAME = "myapp.db"


def _connect(db_name: str) -> sqlite3.Connection:
    """Create a SQLite connection with sensible defaults for this app."""
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    # Enforce referential integrity
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _create_schema(conn: sqlite3.Connection) -> None:
    """Create the application's tables and indexes."""
    # Notes
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          is_favorite INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    # Tags
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE,
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )

    # Many-to-many join table for notes <-> tags
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS note_tags (
          note_id INTEGER NOT NULL,
          tag_id INTEGER NOT NULL,
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          PRIMARY KEY (note_id, tag_id),
          FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
          FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
    )

    # Indexes for fast filtering/search
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_is_favorite ON notes(is_favorite)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_note_tags_note_id ON note_tags(note_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id ON note_tags(tag_id)")

    # Lightweight full-text search using LIKE is acceptable for small local DB,
    # but indexing helps a bit for prefix scans.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_notes_content ON notes(content)")


def main() -> None:
    """Run the schema initialization."""
    conn = _connect(DB_NAME)
    try:
        with conn:
            _create_schema(conn)
        print("Notes schema initialized successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
