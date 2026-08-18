"""Parser for hh.ru vacancies using their public REST API."""

import asyncio
from datetime import datetime
from typing import List, Optional

import aiohttp

from src.config import HH_API_BASE_URL, HH_SEARCH_KEYWORDS, HH_PER_PAGE, HH_ONLY_REMOTE
from src.models import Vacancy
from src.parsers.base import BaseParser


class HHParser(BaseParser):
    """Fetches vacancies from hh.ru for a predefined list of keywords."""

    source_name = "hh.ru"

    async def parse(self) -> List[Vacancy]:
        """Run searches for all configured keywords concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._search_by_keyword(session, keyword)
                for keyword in HH_SEARCH_KEYWORDS
            ]
            results = await asyncio.gather(*tasks)

        # Flatten list of lists into a single list of vacancies
        all_vacancies = [vacancy for group in results for vacancy in group]
        return all_vacancies

    async def _search_by_keyword(
        self, session: aiohttp.ClientSession, keyword: str
    ) -> List[Vacancy]:
        """Fetch vacancies for a single keyword (first page only, for now)."""
        params = {
            "text": keyword,
            "per_page": HH_PER_PAGE,
            "page": 0,
        }
        if HH_ONLY_REMOTE:
            params["schedule"] = "remote"

        url = f"{HH_API_BASE_URL}/vacancies"

        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

        return [self._to_vacancy(item) for item in data.get("items", [])]

    @staticmethod
    def _to_vacancy(item: dict) -> Vacancy:
        """Convert a raw hh.ru API item into a Vacancy object."""
        salary = item.get("salary") or {}
        employer = item.get("employer") or {}
        area = item.get("area") or {}

        published_at: Optional[datetime] = None
        if item.get("published_at"):
            published_at = datetime.fromisoformat(item["published_at"])

        return Vacancy(
            title=item["name"],
            source="hh.ru",
            url=item["alternate_url"],
            company=employer.get("name"),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency"),
            city=area.get("name"),
            published_at=published_at,
            external_id=item["id"],
        )
