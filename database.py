import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

DB_NAME="chat.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn=get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL
    """)
    conn.commit()
    conn.close()
def save_message(role, content):
    conn = get_connection()

    conn.execute(
        "INSERT INTO chat_history (role, content) VALUES (?, ?)",
        (role, content)
    )

    conn.commit()
    conn.close()
def load_history(limit=6):

    conn = get_connection()

    rows = conn.execute("""
        SELECT role, content
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    rows.reverse()

    history = []

    for role, content in rows:
        if role == "user":
            history.append(HumanMessage(content=content))

        else:
            history.append(AIMessage(content=content))

    return history