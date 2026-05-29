"""
Database module for both Smart Judicial Case Timeline Analyzer (Judicial OS) 
and Cyberbullying App WhatsApp (Aegis AI Shield).
Handles SQLite schemas, connections, and CRUD operations for both databases in parallel.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
JUDICIAL_DB_PATH = os.path.join(DB_DIR, "judicial.db")
CYBER_DB_PATH = os.path.join(DB_DIR, "cyberbullying.db")


# ══════════════════════════════════════════════════════════
#  CONNECTION HELPERS
# ══════════════════════════════════════════════════════════

def get_connection():
    """Fallback connection pointing to judicial database by default."""
    return get_judicial_connection()


def get_judicial_connection():
    """Get a connection to the Judicial database with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(JUDICIAL_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_whatsapp_connection():
    """Get a connection to the WhatsApp cyberbullying database with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(CYBER_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ══════════════════════════════════════════════════════════
#  DATABASE INITIALIZATIONS
# ══════════════════════════════════════════════════════════

def init_db():
    """Initialize both schemas in parallel."""
    init_judicial_db()
    init_whatsapp_db()


def init_judicial_db():
    """Initialize the Judicial database schema."""
    conn = get_judicial_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            court TEXT DEFAULT 'Supreme Court of India',
            judge TEXT,
            petitioner TEXT,
            respondent TEXT,
            case_type TEXT DEFAULT 'Civil',
            filing_date TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Normal',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            filename TEXT NOT NULL,
            original_name TEXT,
            file_type TEXT,
            extracted_text TEXT,
            ocr_confidence REAL DEFAULT 0.0,
            word_count INTEGER DEFAULT 0,
            upload_date TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS summaries (
            summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            case_id INTEGER,
            summary_text TEXT,
            key_points TEXT,
            method TEXT DEFAULT 'extractive',
            generated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE,
            FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS timeline_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            event_date TEXT NOT NULL,
            event_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            details TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


def init_whatsapp_db():
    """Initialize the Cyberbullying WhatsApp database schema."""
    conn = get_whatsapp_connection()
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
        # Contact 1 is Aarav, Contact 2 is Priya
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


# ══════════════════════════════════════════════════════════
#  JUDICIAL OS DATABASE METHODS
# ══════════════════════════════════════════════════════════

def create_case(case_number, title, court=None, judge=None, petitioner=None,
                respondent=None, case_type="Civil", filing_date=None,
                status="Pending", priority="Normal"):
    """Create a new case in the judicial database."""
    conn = get_judicial_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cases (case_number, title, court, judge, petitioner,
                          respondent, case_type, filing_date, status, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (case_number, title, court or "Supreme Court of India", judge,
          petitioner, respondent, case_type, filing_date, status, priority))
    conn.commit()
    case_id = cursor.lastrowid
    conn.close()
    return case_id


def get_all_cases():
    """Get all cases as a list of dicts."""
    conn = get_judicial_connection()
    rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case(case_id):
    """Get a single case by ID."""
    conn = get_judicial_connection()
    row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_case_status(case_id, status):
    """Update case status."""
    conn = get_judicial_connection()
    conn.execute("UPDATE cases SET status = ?, updated_at = datetime('now') WHERE case_id = ?",
                 (status, case_id))
    conn.commit()
    conn.close()


def delete_case(case_id):
    """Delete a case and all related records."""
    conn = get_judicial_connection()
    conn.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()


def get_case_stats():
    """Get dashboard statistics for Judicial OS."""
    conn = get_judicial_connection()
    stats = {
        "total_cases": conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0],
        "pending": conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'Pending'").fetchone()[0],
        "disposed": conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'Disposed'").fetchone()[0],
        "hearing": conn.execute("SELECT COUNT(*) FROM cases WHERE status = 'Hearing'").fetchone()[0],
        "total_documents": conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0],
        "total_summaries": conn.execute("SELECT COUNT(*) FROM summaries").fetchone()[0],
    }
    conn.close()
    return stats


def save_document(case_id, filename, original_name, file_type,
                  extracted_text="", ocr_confidence=0.0, word_count=0):
    """Save a document record in Judicial OS."""
    conn = get_judicial_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (case_id, filename, original_name, file_type,
                              extracted_text, ocr_confidence, word_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (case_id, filename, original_name, file_type,
          extracted_text, ocr_confidence, word_count))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id


def get_documents_by_case(case_id):
    """Get all documents for a case."""
    conn = get_judicial_connection()
    rows = conn.execute(
        "SELECT * FROM documents WHERE case_id = ? ORDER BY upload_date DESC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document(doc_id):
    """Get a single document."""
    conn = get_judicial_connection()
    row = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_documents():
    """Get all documents."""
    conn = get_judicial_connection()
    rows = conn.execute("""
        SELECT d.*, c.case_number, c.title as case_title
        FROM documents d
        LEFT JOIN cases c ON d.case_id = c.case_id
        ORDER BY d.upload_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_summary(doc_id, case_id, summary_text, key_points, method="extractive"):
    """Save a summary record."""
    conn = get_judicial_connection()
    cursor = conn.cursor()
    key_points_json = json.dumps(key_points) if isinstance(key_points, (list, dict)) else key_points
    cursor.execute("""
        INSERT INTO summaries (doc_id, case_id, summary_text, key_points, method)
        VALUES (?, ?, ?, ?, ?)
    """, (doc_id, case_id, summary_text, key_points_json, method))
    conn.commit()
    summary_id = cursor.lastrowid
    conn.close()
    return summary_id


def get_summaries_by_case(case_id):
    """Get all summaries for a case."""
    conn = get_judicial_connection()
    rows = conn.execute(
        "SELECT * FROM summaries WHERE case_id = ? ORDER BY generated_at DESC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_timeline_event(case_id, event_date, event_type, title, description="", details=""):
    """Add a timeline event."""
    conn = get_judicial_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO timeline_events (case_id, event_date, event_type, title, description, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (case_id, event_date, event_type, title, description, details))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id


def get_timeline_events(case_id):
    """Get timeline events for a case, ordered by date."""
    conn = get_judicial_connection()
    rows = conn.execute(
        "SELECT * FROM timeline_events WHERE case_id = ? ORDER BY event_date ASC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case_type_distribution():
    """Get distribution of case types."""
    conn = get_judicial_connection()
    rows = conn.execute(
        "SELECT case_type, COUNT(*) as count FROM cases GROUP BY case_type"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_status_distribution():
    """Get distribution of case statuses."""
    conn = get_judicial_connection()
    rows = conn.execute(
        "SELECT status, COUNT(*) as count FROM cases GROUP BY status"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_filings():
    """Get monthly filing counts."""
    conn = get_judicial_connection()
    rows = conn.execute("""
        SELECT strftime('%Y-%m', filing_date) as month, COUNT(*) as count
        FROM cases
        WHERE filing_date IS NOT NULL
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════
#  WHATSAPP SHIELD DATABASE METHODS
# ══════════════════════════════════════════════════════════

def create_contact(name, avatar="👤", toxicity_score=0.0, sent_bully_count=0, received_bully_count=0, is_online=1):
    """Create a new contact in WhatsApp database."""
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
    rows = conn.execute("SELECT * FROM contacts ORDER BY name ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_contact(contact_id):
    """Retrieve a single contact by ID."""
    conn = get_whatsapp_connection()
    row = conn.execute("SELECT * FROM contacts WHERE contact_id = ?", (contact_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def increment_contact_stats(contact_id, stat_type):
    """Increment sent_bully_count, received_bully_count and update toxicity score in WhatsApp."""
    conn = get_whatsapp_connection()
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


def save_message(sender_id, receiver_id, message_text, original_text, is_toxic=0, toxicity_probability=0.0, classification_tag="Safe", is_deleted=0):
    """Save a chat message and return its ID."""
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
    conn.execute("""
        UPDATE messages 
        SET message_text = ?, is_deleted = 1 
        WHERE message_id = ?
    """, (placeholder_text, message_id))
    conn.commit()
    conn.close()


def save_moderation_alert(message_id, rule_triggered, severity="Low", action_taken="Censored"):
    """Save a triggered moderation alert."""
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
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
    conn = get_whatsapp_connection()
    conn.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
    conn.commit()
    conn.close()


def clear_database():
    """Resets database message history and metrics."""
    conn = get_whatsapp_connection()
    conn.execute("DELETE FROM moderation_alerts")
    conn.execute("DELETE FROM messages")
    conn.execute("UPDATE contacts SET toxicity_score = 0.0, sent_bully_count = 0, received_bully_count = 0")
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
#  AUTO-INITIALIZATION
# ══════════════════════════════════════════════════════════

# Initialize both databases upon module import
init_db()
