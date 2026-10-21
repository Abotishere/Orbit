
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("tasks.db")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT
                    (datetime('now', 'localtime'))
            )
        """)


def get_tasks():
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()


def add_task(title, description, priority, due_date):
    with connect() as conn:
        conn.execute("""
            INSERT INTO tasks
                (title, description, priority, due_date)
            VALUES (?, ?, ?, ?)
        """, (title, description, priority, due_date))


def update_task(task_id, title, description, priority, due_date):
    with connect() as conn:
        conn.execute("""
            UPDATE tasks
            SET title = ?, description = ?,
                priority = ?, due_date = ?
            WHERE id = ?
        """, (title, description, priority, due_date, task_id))


def toggle_task(task_id, completed):
    with connect() as conn:
        conn.execute("""
            UPDATE tasks SET completed = ?
            WHERE id = ?
        """, (int(completed), task_id))


def delete_task(task_id):
    with connect() as conn:
        conn.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )
