import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

DB_NAME="chat.db"

def get_connection():
    return sqlite3.connect(DB_NAME)
def create_table():
    conn=get_connection()

    # for simple single table without session_id
    # conn.execute("""
    # CREATE TABLE IF NOT EXISTS chat_history (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         role TEXT NOT NULL,
    #         content TEXT NOT NULL
    # """)

    # for multi session support
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,

        FOREIGN KEY(session_id)
            REFERENCES sessions(id)
    )
    """)

    conn.commit()
    conn.close()


def save_message(session_id,role, content):
    conn = get_connection()
    # if single table na , this is enough
    # conn.execute(
    #     "INSERT INTO chat_history (role, content) VALUES (?, ?)",
    #     (role, content)
    # )
    conn.execute(
        """
        INSERT INTO chat_history
        (session_id, role, content)

        VALUES (?, ?, ?)
        """,

        (session_id, role, content)
    )


    conn.commit()
    conn.close()

# def load_history(limit=6):

#     conn = get_connection()

#     rows = conn.execute("""
#         SELECT role, content
#         FROM chat_history
#         ORDER BY id DESC
#         LIMIT ?
#     """, (limit,)).fetchall()

#     conn.close()

#     rows.reverse()

#     history = []

#     for role, content in rows:
#         if role == "user":
#             history.append(HumanMessage(content=content))

#         else:
#             history.append(AIMessage(content=content))

#     return history

#load history with session_id , no need revers() as v used order by id
def load_history(session_id):

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT role, content

        FROM chat_history

        WHERE session_id = ?

        ORDER BY id
        """,

        (session_id,)
    ).fetchall()

    conn.close()

    history = []

    for role, content in rows:

        if role == "user":
            history.append(HumanMessage(content=content))
        else:
            history.append(AIMessage(content=content))

    return history

def create_session(name):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO sessions(name) VALUES(?)",
        (name,)
    )

    conn.commit()

    session_id = cursor.lastrowid

    conn.close()

    return session_id

def list_sessions():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, name
        FROM sessions
        ORDER BY id
    """).fetchall()

    conn.close()

    return rows