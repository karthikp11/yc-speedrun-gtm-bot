import sqlite3
import hashlib
from typing import Optional, Dict, Any, List
from config import config

class DatabaseManager:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracked_companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    canonical_domain TEXT,
                    batch_identifier TEXT NOT NULL,
                    program_type TEXT CHECK(program_type IN ('YC_MAIN', 'SPEEDRUN', 'UNKNOWN')) DEFAULT 'YC_MAIN',
                    official_status TEXT CHECK(official_status IN ('CONFIRMED_OFFICIAL', 'EARLY_FOUNDER_SIGNAL')) NOT NULL,
                    source_platform TEXT NOT NULL,
                    source_url TEXT UNIQUE NOT NULL,
                    description TEXT,
                    founder_info TEXT,
                    detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    payload_hash TEXT UNIQUE NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_scanned INTEGER,
                    new_signals INTEGER,
                    status TEXT
                );
            """)
            conn.commit()

    @staticmethod
    def generate_hash(company_name: str, source_url: str) -> str:
        raw_key = f"{company_name.lower().strip()}:{source_url.lower().strip()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def is_signal_processed(self, payload_hash: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM tracked_companies WHERE payload_hash = ?", (payload_hash,))
            return cursor.fetchone() is not None

    def insert_signal(self, data: Dict[str, Any]) -> bool:
        payload_hash = self.generate_hash(data["company_name"], data["source_url"])
        if self.is_signal_processed(payload_hash):
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tracked_companies (
                    company_name, canonical_domain, batch_identifier, program_type,
                    official_status, source_platform, source_url, description,
                    founder_info, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["company_name"],
                data.get("canonical_domain", ""),
                data["batch_identifier"],
                data.get("program_type", "YC_MAIN"),
                data["official_status"],
                data["source_platform"],
                data["source_url"],
                data.get("description", ""),
                data.get("founder_info", ""),
                payload_hash
            ))
            conn.commit()
            return True

    def record_metrics(self, scanned: int, new_signals: int, status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO execution_metrics (total_scanned, new_signals, status) VALUES (?, ?, ?)",
                (scanned, new_signals, status)
            )
            conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM tracked_companies")
            total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) as early FROM tracked_companies WHERE official_status='EARLY_FOUNDER_SIGNAL'")
            early = cursor.fetchone()["early"]
            return {"total_companies_tracked": total, "early_signals_caught": early}
