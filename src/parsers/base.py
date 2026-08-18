"""Base interface that every vacancy source parser must implement."""

from abc import ABC, abstractmethod
from typing import List

from src.models import Vacancy


class BaseParser(ABC):
    """Abstract base class for all vacancy parsers.

    Every concrete parser (hh.ru, Telegram, etc.) must implement
    the `parse` method and return a list of Vacancy objects.
    """

    source_name: str = "unknown"

    @abstractmethod
    async def parse(self) -> List[Vacancy]:
        """Fetch and return a list of vacancies from this source."""
        raise NotImplementedError
