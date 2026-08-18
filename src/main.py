"""Entry point: run all parsers and store results in the database."""

import asyncio

from src.database import init_db, save_vacancy
from src.parsers.hh_parser import HHParser


async def main() -> None:
    """Initialize the database and run all configured parsers."""
    await init_db()

    parser = HHParser()
    print(f"Fetching vacancies from {parser.source_name}...")

    try:
        vacancies = await parser.parse()
    except Exception as e:
        print(f"Failed to fetch vacancies: {e}")
        return

    print(f"Fetched {len(vacancies)} vacancies total.")

    saved_count = 0
    for vacancy in vacancies:
        was_new = await save_vacancy(vacancy)
        if was_new:
            saved_count += 1

    print(f"Saved {saved_count} new vacancies to the database.")


if __name__ == "__main__":
    asyncio.run(main())
