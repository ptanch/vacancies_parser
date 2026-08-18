"""Async SQLite storage layer for parsed vacancies."""

import aiosqlite
from typing import List, Optional
from pathlib import Path

from src.config import DB_PATH
from src.models import Vacancy


CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS vacancies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    currency TEXT,
    city TEXT,
    description TEXT,
    url TEXT NOT NULL,
    published_at TEXT,
    parsed_at TEXT NOT NULL,
    UNIQUE(source, external_id)
);
"""


async def init_db(db_path: Path = DB_PATH) -> None:
    """Create the vacancies table if it does not exist yet."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_TABLE_QUERY)
        await db.commit()


async def save_vacancy(vacancy: Vacancy, db_path: Path = DB_PATH) -> bool:
    """Insert a vacancy into the database.

    Duplicates are silently skipped based on the (source, external_id)
    unique constraint. Returns True if a new row was inserted, False if
    the vacancy already existed.
    """
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute(
            """
            INSERT OR IGNORE INTO vacancies (
                external_id, source, title, company,
                salary_from, salary_to, currency, city,
                description, url, published_at, parsed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vacancy.external_id,
                vacancy.source,
                vacancy.title,
                vacancy.company,
                vacancy.salary_from,
                vacancy.salary_to,
                vacancy.currency,
                vacancy.city,
                vacancy.description,
                vacancy.url,
                vacancy.published_at.isoformat() if vacancy.published_at else None,
                vacancy.parsed_at.isoformat(),
            ),
        )
        await db.commit()
        return cursor.rowcount > 0


async def get_all_vacancies(
    source: Optional[str] = None, db_path: Path = DB_PATH
) -> List[dict]:
    """Fetch all vacancies, optionally filtered by source.

    Returns a list of plain dicts (row -> dict), which is convenient
    for later export to CSV/Excel or for a future API layer.
    """
    query = "SELECT * FROM vacancies"
    params: tuple = ()

    if source:
        query += " WHERE source = ?"
        params = (source,)

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
