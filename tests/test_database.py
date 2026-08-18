"""Tests for the async SQLite storage layer."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.database import init_db, save_vacancy, get_all_vacancies
from src.models import Vacancy


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Provide a temporary, isolated SQLite file for each test."""
    return tmp_path / "test_vacancies.db"


def make_vacancy(external_id: str = "123", source: str = "hh.ru") -> Vacancy:
    """Build a sample Vacancy for tests."""
    return Vacancy(
        title="Python Developer",
        source=source,
        url="https://example.com/vacancy/123",
        company="Test Company",
        salary_from=100000,
        salary_to=150000,
        currency="RUR",
        city="Moscow",
        published_at=datetime.now(timezone.utc),
        external_id=external_id,
    )


async def test_init_db_creates_table(temp_db_path: Path) -> None:
    """init_db should run without errors and create an empty table."""
    await init_db(db_path=temp_db_path)
    vacancies = await get_all_vacancies(db_path=temp_db_path)
    assert vacancies == []


async def test_save_vacancy_inserts_new_row(temp_db_path: Path) -> None:
    """Saving a new vacancy should succeed and be retrievable."""
    await init_db(db_path=temp_db_path)
    vacancy = make_vacancy()

    was_inserted = await save_vacancy(vacancy, db_path=temp_db_path)
    assert was_inserted is True

    vacancies = await get_all_vacancies(db_path=temp_db_path)
    assert len(vacancies) == 1
    assert vacancies[0]["title"] == "Python Developer"


async def test_save_vacancy_skips_duplicate(temp_db_path: Path) -> None:
    """Saving the same (source, external_id) twice should not duplicate it."""
    await init_db(db_path=temp_db_path)
    vacancy = make_vacancy()

    await save_vacancy(vacancy, db_path=temp_db_path)
    was_inserted_again = await save_vacancy(vacancy, db_path=temp_db_path)

    assert was_inserted_again is False

    vacancies = await get_all_vacancies(db_path=temp_db_path)
    assert len(vacancies) == 1


async def test_get_all_vacancies_filters_by_source(temp_db_path: Path) -> None:
    """get_all_vacancies(source=...) should only return matching rows."""
    await init_db(db_path=temp_db_path)

    await save_vacancy(make_vacancy(external_id="1", source="hh.ru"), db_path=temp_db_path)
    await save_vacancy(make_vacancy(external_id="2", source="telegram"), db_path=temp_db_path)

    hh_vacancies = await get_all_vacancies(source="hh.ru", db_path=temp_db_path)
    assert len(hh_vacancies) == 1
    assert hh_vacancies[0]["source"] == "hh.ru"
