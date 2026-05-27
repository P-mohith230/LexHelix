"""
Database module for Smart Judicial Case Timeline Analyzer.
Handles SQLite database creation, connection, and CRUD operations.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
DB_PATH = os.path.join(DB_DIR, "judicial.db")


def get_connection():
    """Get a database connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with schema."""
    conn = get_connection()
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


# ── Case CRUD ──────────────────────────────────────────────

def create_case(case_number, title, court=None, judge=None, petitioner=None,
                respondent=None, case_type="Civil", filing_date=None,
                status="Pending", priority="Normal"):
    """Create a new case and return its ID."""
    conn = get_connection()
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
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cases ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case(case_id):
    """Get a single case by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_case_status(case_id, status):
    """Update case status."""
    conn = get_connection()
    conn.execute("UPDATE cases SET status = ?, updated_at = datetime('now') WHERE case_id = ?",
                 (status, case_id))
    conn.commit()
    conn.close()


def delete_case(case_id):
    """Delete a case and all related records."""
    conn = get_connection()
    conn.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()


def get_case_stats():
    """Get dashboard statistics."""
    conn = get_connection()
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


# ── Document CRUD ──────────────────────────────────────────

def save_document(case_id, filename, original_name, file_type,
                  extracted_text="", ocr_confidence=0.0, word_count=0):
    """Save a document record."""
    conn = get_connection()
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
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM documents WHERE case_id = ? ORDER BY upload_date DESC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_document(doc_id):
    """Get a single document."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_documents():
    """Get all documents."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT d.*, c.case_number, c.title as case_title
        FROM documents d
        LEFT JOIN cases c ON d.case_id = c.case_id
        ORDER BY d.upload_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Summary CRUD ───────────────────────────────────────────

def save_summary(doc_id, case_id, summary_text, key_points, method="extractive"):
    """Save a summary record."""
    conn = get_connection()
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
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM summaries WHERE case_id = ? ORDER BY generated_at DESC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Timeline CRUD ──────────────────────────────────────────

def add_timeline_event(case_id, event_date, event_type, title, description="", details=""):
    """Add a timeline event."""
    conn = get_connection()
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
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM timeline_events WHERE case_id = ? ORDER BY event_date ASC",
        (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case_type_distribution():
    """Get distribution of case types."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT case_type, COUNT(*) as count FROM cases GROUP BY case_type"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_status_distribution():
    """Get distribution of case statuses."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT status, COUNT(*) as count FROM cases GROUP BY status"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_filings():
    """Get monthly filing counts."""
    conn = get_connection()
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


# Initialize the database on import
init_db()
