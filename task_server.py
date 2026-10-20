
import sqlite3
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer(
    "Task Manager",
    instructions="Manage the user's personal tasks."
)

DB_PATH = Path(__file__).parent / "tasks.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


@mcp.tool()
def add_task(title: str) -> dict:
    """Create a new task with the specified title."""
    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        task_id = cursor.lastrowid

    return {
        "id": task_id,
        "title": title,
        "completed": False
    }


@mcp.tool()
def list_tasks() -> list[dict]:
    """Return all tasks and their completion status."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id"
        ).fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "completed": bool(row["completed"])
        }
        for row in rows
    ]


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark an existing task as completed."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Task {task_id} does not exist.")

    return {"task_id": task_id, "completed": True}


if __name__ == "__main__":
    initialize_database()
    mcp.run()
