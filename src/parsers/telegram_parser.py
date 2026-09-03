"""Parser for public Telegram channels using their web preview pages.

Uses the public https://t.me/s/<channel> pages, which require no
authentication or API credentials. Only the most recent ~20 messages
per channel are available this way.
"""

import asyncio
import re
from datetime import datetime
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup

from src.config import TELEGRAM_BASE_URL, TELEGRAM_CHANNELS
from src.models import Vacancy
from src.parsers.base import BaseParser


class TelegramParser(BaseParser):
    """Fetches recent posts from public Telegram channels via web preview."""

    source_name = "telegram"

    async def parse(self) -> List[Vacancy]:
        """Fetch posts from all configured channels concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_channel(session, channel)
                for channel in TELEGRAM_CHANNELS
            ]
            results = await asyncio.gather(*tasks)

        all_vacancies = [vacancy for group in results for vacancy in group]
        return all_vacancies

    async def _fetch_channel(
        self, session: aiohttp.ClientSession, channel: str
    ) -> List[Vacancy]:
        """Fetch and parse recent posts from a single channel."""
        url = f"{TELEGRAM_BASE_URL}/{channel}"

        async with session.get(url) as response:
            if response.status != 200:
                print(f"Failed to fetch {channel}: HTTP {response.status}")
                return []
            html = await response.text()

        return self._parse_html(html, channel)

    def _parse_html(self, html: str, channel: str) -> List[Vacancy]:
        """Extract individual posts from the channel preview HTML."""
        soup = BeautifulSoup(html, "html.parser")
        messages = soup.select("div.tgme_widget_message")

        vacancies = []
        for message in messages:
            vacancy = self._message_to_vacancy(message, channel)
            if vacancy:
                vacancies.append(vacancy)
        return vacancies

    def _message_to_vacancy(self, message, channel: str) -> Optional[Vacancy]:
        """Convert a single message block into a Vacancy object."""
        text_el = message.select_one("div.tgme_widget_message_text")
        if not text_el:
            return None  # skip posts without text (photos, stickers, etc.)

        text = text_el.get_text(separator="\n").strip()
        if not text:
            return None

        # The message id is embedded in the data-post attribute,
        # e.g. data-post="channelname/1234"
        post_id = message.get("data-post", "")
        external_id = post_id.split("/")[-1] if "/" in post_id else post_id

        link_el = message.select_one("a.tgme_widget_message_date")
        url = link_el["href"] if link_el else f"https://t.me/{channel}"

        time_el = message.select_one("time.time")
        published_at = None
        if time_el and time_el.get("datetime"):
            published_at = datetime.fromisoformat(time_el["datetime"])

        # First non-empty line as a rough "title" — channel posts are free
        # text, not structured, so this is a heuristic, not a guarantee.
        first_line = text.split("\n")[0][:200]

        return Vacancy(
            title=first_line,
            source="telegram",
            url=url,
            description=text,
            published_at=published_at,
            external_id=external_id,
        )
