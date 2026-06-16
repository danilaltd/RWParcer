

import sqlite3
from datetime import datetime, timezone
from ProxyTypes import ProxyDTO

class ProxyDatabase:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS proxies (
                    ip_port TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    latency INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def save_results(self, rows: list[ProxyDTO]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO proxies (ip_port, status, updated_at, latency)
                VALUES (?, ?, datetime('now'), ?)
                ON CONFLICT(ip_port) DO UPDATE SET
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    latency = excluded.latency
                """,
                [(proxy.url, proxy.status.value, proxy.latency) for proxy in rows],
            )
            conn.commit()

    def clear_old(self, ttl_hours: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                DELETE FROM proxies 
                WHERE updated_at < datetime('now', '-' || ? || ' hours')
                """,
                (ttl_hours,)
            )
            conn.commit()
        return cursor.rowcount

    def get_active_proxies(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT ip_port FROM proxies WHERE status = 'active' ORDER BY latency ASC, ip_port ASC"
            ).fetchall()
            return [row[0] for row in rows]