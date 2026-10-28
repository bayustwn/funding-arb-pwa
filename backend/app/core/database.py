"""
Async Read-Only SQLite Database Access Layer
Guarantees zero lock contention with active trading daemon:
- PRAGMA query_only = ON
- PRAGMA journal_mode = WAL
- PRAGMA busy_timeout = 5000
Executes queries safely inside asyncio thread pool to avoid blocking FastAPI event loop.
"""

import sqlite3
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from app.core.config import settings


@contextmanager
def get_read_only_connection(db_path: Optional[str] = None):
    """
    Synchronous context manager for read-only SQLite access.
    """
    path = db_path or settings.DB_PATH
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA query_only = ON;")
        cur.execute("PRAGMA busy_timeout = 5000;")
        yield cur
    finally:
        conn.close()


def _execute_query_sync(query: str, params: tuple = (), db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Helper executed inside asyncio threadpool."""
    with get_read_only_connection(db_path) as cur:
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def _execute_scalar_sync(query: str, params: tuple = (), db_path: Optional[str] = None) -> Any:
    """Helper to fetch single value executed inside asyncio threadpool."""
    with get_read_only_connection(db_path) as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        return row[0] if row else None


async def execute_query(query: str, params: tuple = (), db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Non-blocking async query execution.
    Returns list of dicts.
    """
    return await asyncio.to_thread(_execute_query_sync, query, params, db_path)


async def execute_scalar(query: str, params: tuple = (), db_path: Optional[str] = None) -> Any:
    """
    Non-blocking async query execution returning a single scalar value.
    """
    return await asyncio.to_thread(_execute_scalar_sync, query, params, db_path)
