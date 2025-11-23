from mcp.server.fastmcp import FastMCP
import sqlite3
from app import db as app_db

mcp = FastMCP("UtilityTools")


# -------------------------------------------------------------------
# Core Notes Database Logic (with long semantic docstrings)
# -------------------------------------------------------------------

def create_note(title: str, body: str) -> int:
    """
    Insert a new note into the database.

    Args:
        title (str): The title of the note.
        body (str): The body or content of the note.

    Returns:
        int: The auto-generated ID of the created note.

    Use cases:
        - Personal note-taking
        - Storing logs or documentation
        - Knowledge bases
        - RAG document repositories
    """
    conn = app_db.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    return cur.lastrowid


def list_notes():
    """
    Retrieve all notes from the database sorted by newest first.

    Returns:
        list[dict]: A list of notes where each note contains:
            id, title, body

    Useful for:
        - Displaying a note index
        - Running embeddings over multiple notes
        - Full-text searching and semantic retrieval
    """
    conn = app_db.get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def get_note(nid: int):
    """
    Retrieve a single note by its numerical ID.

    Args:
        nid (int): Unique identifier of the note.

    Returns:
        dict | None: The note if found, else None.

    Semantic use:
        - Fetch individual documents for RAG
        - Metadata retrieval
        - User-indexed document access
    """
    conn = app_db.get_conn()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM notes WHERE id = ?", (nid,)).fetchone()
    return dict(row) if row else None


# -------------------------------------------------------------------
# MCP Tool
# -------------------------------------------------------------------

@mcp.tool()
def notes(action: str, title: str = "", body: str = "", id: int = 0):
    """
    Notes management tool supporting CRUD-like operations.

    Supported actions:
        - create: Creates a note using (title, body)
        - list: Returns all notes
        - get: Returns a note by numeric ID

    Args:
        action (str): One of ["create", "list", "get"]
        title (str, optional): Title used only for creation.
        body (str, optional): Body used only for creation.
        id (int, optional): Note ID used only for "get".

    Returns:
        dict or list: Depending on action.

    Semantic relevance:
        - Perfect for structured memory storage
        - Excellent for chunking text for embeddings
        - Works well in RAG workflows
    """
    action = action.lower()

    if action == "create":
        return {"id": create_note(title, body)}

    if action == "list":
        return {"notes": list_notes()}

    if action == "get":
        note = get_note(id)
        return note if note else {"error": "not found"}

    raise ValueError("Unknown action")
