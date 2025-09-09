import os
import psycopg2
from psycopg2.extras import DictCursor

def get_db_connection():
    """Create a PostgreSQL connection using environment variables."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "babydb"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        port=os.getenv("POSTGRES_PORT", 5432)
    )


def init_db():
    """Initialize database schema for conversations and feedback."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id UUID REFERENCES conversations(id),
                    feedback INTEGER CHECK (feedback IN (-1, 1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    finally:
        conn.close()


def save_conversation(conversation_id, question, answer):
    """Save a conversation record."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (id, question, answer)
                VALUES (%s, %s, %s);
                """,
                (conversation_id, question, answer)
            )
        conn.commit()
    finally:
        conn.close()


def save_feedback(conversation_id, feedback):
    """Save user feedback (-1 or +1) for a conversation."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (conversation_id, feedback)
                VALUES (%s, %s);
                """,
                (conversation_id, feedback)
            )
        conn.commit()
    finally:
        conn.close()
