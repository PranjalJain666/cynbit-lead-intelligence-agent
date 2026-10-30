import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.config import settings

def get_connection() -> sqlite3.Connection:
    """Creates and returns a connection to SQLite with row factory."""
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if not present."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inquiries (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                company_name TEXT,
                project_description TEXT NOT NULL,
                budget_inr REAL,
                timeline TEXT,
                service_category TEXT NOT NULL,
                priority_tier TEXT NOT NULL,
                total_score REAL NOT NULL,
                full_data_json TEXT NOT NULL
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiries_priority ON inquiries(priority_tier)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inquiries_timestamp ON inquiries(timestamp)")
        conn.commit()
    finally:
        conn.close()

def save_inquiry(data: Dict[str, Any]) -> str:
    """Saves a fully analyzed inquiry into SQLite."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        lead_score = data.get("lead_score", {})
        cursor.execute(
            """
            INSERT OR REPLACE INTO inquiries (
                id, timestamp, customer_name, email, company_name,
                project_description, budget_inr, timeline,
                service_category, priority_tier, total_score, full_data_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["inquiry_id"],
                data["timestamp"],
                data["customer_name"],
                data["email"],
                data.get("company_name"),
                data["original_description"],
                data.get("budget_inr"),
                data.get("timeline"),
                data["service_category"],
                lead_score.get("priority_tier", "Medium"),
                lead_score.get("total_score", 0.0),
                json.dumps(data)
            )
        )
        conn.commit()
        return data["inquiry_id"]
    finally:
        conn.close()

def get_inquiry(inquiry_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single inquiry by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT full_data_json FROM inquiries WHERE id = ?", (inquiry_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row["full_data_json"])
        return None
    finally:
        conn.close()

def list_inquiries(limit: int = 100, priority: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists recent inquiries with optional priority filtering."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if priority and isinstance(priority, str):
            cursor.execute(
                """
                SELECT id, timestamp, customer_name, company_name,
                       service_category, priority_tier, total_score,
                       budget_inr, timeline
                FROM inquiries
                WHERE UPPER(priority_tier) = UPPER(?)
                ORDER BY timestamp DESC LIMIT ?
                """,
                (priority, limit)
            )
        else:
            cursor.execute(
                """
                SELECT id, timestamp, customer_name, company_name,
                       service_category, priority_tier, total_score,
                       budget_inr, timeline
                FROM inquiries
                ORDER BY timestamp DESC LIMIT ?
                """,
                (limit,)
            )
        rows = cursor.fetchall()
        return [
            {
                "inquiry_id": row["id"],
                "timestamp": row["timestamp"],
                "customer_name": row["customer_name"],
                "company_name": row["company_name"],
                "service_category": row["service_category"],
                "priority_tier": row["priority_tier"],
                "total_score": row["total_score"],
                "budget_inr": row["budget_inr"],
                "timeline": row["timeline"],
            }
            for row in rows
        ]
    finally:
        conn.close()

def delete_inquiry(inquiry_id: str) -> bool:
    """Deletes an inquiry by ID."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inquiries WHERE id = ?", (inquiry_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def count_inquiries() -> int:
    """Returns the total number of stored inquiries."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inquiries")
        return cursor.fetchone()[0]
    finally:
        conn.close()
