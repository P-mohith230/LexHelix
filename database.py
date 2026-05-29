"""
Database module for Cyberbullying App WhatsApp.
Handles SQLite database creation, connection, and CRUD operations.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
DB_PATH = os.path.join(DB_DIR, "cyberbullying.db")


def get_connection():
    """Get a database connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with the schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS contacts (
            contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar TEXT,
            toxicity_score REAL DEFAULT 0.0,
            sent_bully_count INTEGER DEFAULT 0,
            received_bully_count INTEGER DEFAULT 0,
            is_online INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            original_text TEXT NOT NULL,
            is_toxic INTEGER DEFAULT 0,
            toxicity_probability REAL DEFAULT 0.0,
            classification_tag TEXT DEFAULT 'Safe',
            is_deleted INTEGER DEFAULT 0,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (sender_id) REFERENCES contacts(contact_id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES contacts(contact_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS moderation_alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            rule_triggered TEXT NOT NULL,
            severity TEXT DEFAULT 'Low',
            action_taken TEXT DEFAULT 'None',
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE
        );
    """)

    # Seed contacts if database is empty
    cursor.execute("SELECT COUNT(*) FROM contacts")
    if cursor.fetchone()[0] == 0:
        seed_contacts = [
            ("Aarav Sharma", "👨‍💼", 0.0, 0, 0, 1),
            ("Priya Patel", "👩‍💻", 0.0, 0, 0, 1),
            ("Rohan Das", "👨‍🎨", 0.0, 0, 0, 1),
            ("Ananya Rao", "👩‍⚕️", 0.0, 0, 0, 0),
            ("Kabir Singh", "🎸", 0.0, 0, 0, 1),
        ]
        cursor.executemany("""
            INSERT INTO contacts (name, avatar, toxicity_score, sent_bully_count, received_bully_count, is_online)
            VALUES (?, ?, ?, ?, ?, ?)
        """, seed_contacts)

        # Seed initial message history
        # Contact 1 is Aarav, Contact 2 is Priya, Contact 3 is Rohan
        seed_messages = [
            (1, 2, "Hey Priya, did you check the new project specs?", "Hey Priya, did you check the new project specs?", 0, 0.02, "Safe", 0),
            (2, 1, "Yes Aarav! Designing the WebGL interface right now.", "Yes Aarav! Designing the WebGL interface right now.", 0, 0.01, "Safe", 0),
            (3, 1, "Rohan here! Excited to join the workspace.", "Rohan here! Excited to join the workspace.", 0, 0.02, "Safe", 0),
        ]
        cursor.executemany("""
            INSERT INTO messages (sender_id, receiver_id, message_text, original_text, is_toxic, toxicity_probability, classification_tag, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_messages)

    conn.commit()
    conn.close()


# ── Contact Helper Methods ─────────────────────────────────

def create_contact(name, avatar="👤", toxicity_score=0.0, sent_bully_count=0, received_bully_count=0, is_online=1):
    """Create a new contact and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contacts (name, avatar, toxicity_score, sent_bully_count, received_bully_count, is_online)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, avatar, toxicity_score, sent_bully_count, received_bully_count, is_online))
    conn.commit()
    contact_id = cursor.lastrowid
    conn.close()
    return contact_id


def get_all_contacts():
    """Retrieve all contacts as a list of dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM contacts ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contact(contact_id):
    """Retrieve a single contact by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM contacts WHERE contact_id = ?", (contact_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_contact_stats(contact_id, stat_type):
    """Increment sent_bully_count, received_bully_count or update toxicity score."""
    conn = get_connection()
    if stat_type == "sent":
        conn.execute("UPDATE contacts SET sent_bully_count = sent_bully_count + 1 WHERE contact_id = ?", (contact_id,))
    elif stat_type == "received":
        conn.execute("UPDATE contacts SET received_bully_count = received_bully_count + 1 WHERE contact_id = ?", (contact_id,))
    
    # Recalculate toxicity score based on total sent messages vs bullying sent messages
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE sender_id = ?", (contact_id,))
    total_msgs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE sender_id = ? AND is_toxic = 1", (contact_id,))
    toxic_msgs = cursor.fetchone()[0]
    
    if total_msgs > 0:
        new_score = round(float(toxic_msgs) / total_msgs, 2)
        conn.execute("UPDATE contacts SET toxicity_score = ? WHERE contact_id = ?", (new_score, contact_id))

    conn.commit()
    conn.close()


# ── Message Helper Methods ─────────────────────────────────

def save_message(sender_id, receiver_id, message_text, original_text, is_toxic=0, toxicity_probability=0.0, classification_tag="Safe", is_deleted=0):
    """Save a chat message and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, message_text, original_text, is_toxic, toxicity_probability, classification_tag, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (sender_id, receiver_id, message_text, original_text, is_toxic, toxicity_probability, classification_tag, is_deleted))
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    return message_id


def get_chat_history(contact_a, contact_b):
    """Get all non-deleted or censored messages exchanged between two contacts."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (contact_a, contact_b, contact_b, contact_a)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def flag_message_deleted(message_id, placeholder_text="[Message deleted - flagged as cyberbullying]"):
    """Censor/delete a message content permanently in the DB after countdown."""
    conn = get_connection()
    conn.execute("""
        UPDATE messages 
        SET message_text = ?, is_deleted = 1 
        WHERE message_id = ?
    """, (placeholder_text, message_id))
    conn.commit()
    conn.close()


# ── Moderation Helper Methods ──────────────────────────────

def save_moderation_alert(message_id, rule_triggered, severity="Low", action_taken="Censored"):
    """Save a triggered moderation alert."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO moderation_alerts (message_id, rule_triggered, severity, action_taken)
        VALUES (?, ?, ?, ?)
    """, (message_id, rule_triggered, severity, action_taken))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id


def get_all_alerts():
    """Get all moderation logs with sender/receiver details."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, m.original_text, m.toxicity_probability, 
               s.name as sender_name, r.name as receiver_name
        FROM moderation_alerts a
        JOIN messages m ON a.message_id = m.message_id
        JOIN contacts s ON m.sender_id = s.contact_id
        JOIN contacts r ON m.receiver_id = r.contact_id
        ORDER BY a.timestamp DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_moderation_stats():
    """Retrieve statistical counters to feed the WebGL charts."""
    conn = get_connection()
    stats = {
        "total_messages": conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
        "safe_messages": conn.execute("SELECT COUNT(*) FROM messages WHERE is_toxic = 0").fetchone()[0],
        "toxic_messages": conn.execute("SELECT COUNT(*) FROM messages WHERE is_toxic = 1").fetchone()[0],
        "categories": {
            "Threat": conn.execute("SELECT COUNT(*) FROM messages WHERE classification_tag = 'Threat'").fetchone()[0],
            "Insult": conn.execute("SELECT COUNT(*) FROM messages WHERE classification_tag = 'Insult'").fetchone()[0],
            "Harassment": conn.execute("SELECT COUNT(*) FROM messages WHERE classification_tag = 'Harassment'").fetchone()[0],
            "Hate Speech": conn.execute("SELECT COUNT(*) FROM messages WHERE classification_tag = 'Hate Speech'").fetchone()[0],
            "Safe": conn.execute("SELECT COUNT(*) FROM messages WHERE classification_tag = 'Safe'").fetchone()[0],
        }
    }
    conn.close()
    return stats

def delete_contact(contact_id):
    """Delete a contact and all related messages / alerts via cascade."""
    conn = get_connection()
    conn.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
    conn.commit()
    conn.close()


def clear_database():
    """Resets database message history and metrics."""
    conn = get_connection()
    conn.execute("DELETE FROM moderation_alerts")
    conn.execute("DELETE FROM messages")
    conn.execute("UPDATE contacts SET toxicity_score = 0.0, sent_bully_count = 0, received_bully_count = 0")
    conn.commit()
    conn.close()


# Initialize database upon import
init_db()
