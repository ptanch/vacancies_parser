from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Vacancy:
    """Job structure, regardless of source"""

    title: str                      # job title
    source: str                     # "hh.ru", "telegram", "linkedin"
    url: str                        # link to the job vacancy

    company: Optional[str] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    currency: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None

    published_at: Optional[datetime] = None
    parsed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # A unique identifier from an external source (job ID on hh.ru,
    # Telegram message ID, etc.) — required to avoid saving duplicates.
    external_id: Optional[str] = None
