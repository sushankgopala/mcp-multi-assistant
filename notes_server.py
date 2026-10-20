
import json
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer(
    "Notes Server",
    instructions="Save and search the user's personal notes."
)

NOTES_FILE = Path(__file__).parent / "notes.json"


def load_notes() -> list[dict]:
    """Load saved notes, or return an empty list."""
    if not NOTES_FILE.exists():
        return []

    return json.loads(NOTES_FILE.read_text(encoding="utf-8"))


def save_notes(notes: list[dict]) -> None:
    """Write notes to the local JSON file."""
    NOTES_FILE.write_text(
        json.dumps(notes, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


@mcp.tool()
def save_note(title: str, content: str) -> dict:
    """Save a note with a title and its content."""
    title = title.strip()
    content = content.strip()

    if not title:
        raise ValueError("Note title cannot be empty.")

    if not content:
        raise ValueError("Note content cannot be empty.")

    notes = load_notes()

    note_id = max(
        (note["id"] for note in notes),
        default=0
    ) + 1

    note = {
        "id": note_id,
        "title": title,
        "content": content
    }

    notes.append(note)
    save_notes(notes)

    return note


@mcp.tool()
def search_notes(query: str) -> list[dict]:
    """Search saved notes by title or content."""
    query = query.strip().casefold()

    if not query:
        raise ValueError("Search query cannot be empty.")

    notes = load_notes()

    return [
        note for note in notes
        if query in note["title"].casefold()
        or query in note["content"].casefold()
    ]


@mcp.prompt()
def summarize_notes(topic: str) -> str:
    """Create a reusable prompt for summarizing notes about a topic."""
    return (
        f"Summarize the user's notes about: {topic}\n\n"
        "Identify the key ideas, explain important connections, "
        "and list any unanswered questions. "
        "Use only information supported by the notes provided. "
        "Do not invent facts."
    )

if __name__ == "__main__":
    mcp.run()
