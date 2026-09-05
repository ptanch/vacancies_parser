"""Tests for the Telegram channel parser (web preview scraping)."""

import pytest
from aioresponses import aioresponses

from src.parsers.telegram_parser import TelegramParser


SAMPLE_HTML = """
<div class="tgme_widget_message" data-post="testchannel/101">
    <div class="tgme_widget_message_text">
        Python Developer | Remote | Acme Corp<br>Great opportunity for a mid-level dev.
    </div>
    <a class="tgme_widget_message_date" href="https://t.me/testchannel/101">
        <time class="time" datetime="2026-08-20T10:00:00+00:00">10:00</time>
    </a>
</div>
<div class="tgme_widget_message" data-post="testchannel/102">
    <div class="tgme_widget_message_text">
        Data Analyst | Hybrid | Beta LLC
    </div>
    <a class="tgme_widget_message_date" href="https://t.me/testchannel/102">
        <time class="time" datetime="2026-08-20T11:00:00+00:00">11:00</time>
    </a>
</div>
<div class="tgme_widget_message" data-post="testchannel/103">
    <!-- No text block: e.g. a photo-only post, should be skipped -->
</div>
"""


async def test_parse_extracts_vacancies_from_channel() -> None:
    """A channel with 3 posts (2 with text, 1 without) should yield 2 vacancies."""
    parser = TelegramParser(channels=["testchannel"])

    with aioresponses() as mocked:
        mocked.get("https://t.me/s/testchannel", status=200, body=SAMPLE_HTML)
        vacancies = await parser.parse()

    assert len(vacancies) == 2


async def test_parse_extracts_correct_fields() -> None:
    """Fields on the first parsed vacancy should match the sample HTML."""
    parser = TelegramParser(channels=["testchannel"])

    with aioresponses() as mocked:
        mocked.get("https://t.me/s/testchannel", status=200, body=SAMPLE_HTML)
        vacancies = await parser.parse()

    first = vacancies[0]
    assert first.external_id == "101"
    assert first.title == "Python Developer | Remote | Acme Corp"
    assert first.source == "telegram"
    assert first.url == "https://t.me/testchannel/101"
    assert "Great opportunity" in first.description


async def test_parse_skips_posts_without_text() -> None:
    """Posts without a text block (e.g. photo-only) must be skipped, not crash."""
    parser = TelegramParser(channels=["testchannel"])

    with aioresponses() as mocked:
        mocked.get("https://t.me/s/testchannel", status=200, body=SAMPLE_HTML)
        vacancies = await parser.parse()

    ids = [v.external_id for v in vacancies]
    assert "103" not in ids


async def test_parse_handles_non_200_response() -> None:
    """A failing HTTP response (e.g. 404) should return an empty list, not crash."""
    parser = TelegramParser(channels=["nonexistent_channel"])

    with aioresponses() as mocked:
        mocked.get("https://t.me/s/nonexistent_channel", status=404)
        vacancies = await parser.parse()

    assert vacancies == []


async def test_parse_multiple_channels_concurrently() -> None:
    """Vacancies from multiple channels should be combined into one list."""
    parser = TelegramParser(channels=["channel_a", "channel_b"])

    with aioresponses() as mocked:
        mocked.get("https://t.me/s/channel_a", status=200, body=SAMPLE_HTML)
        mocked.get("https://t.me/s/channel_b", status=200, body=SAMPLE_HTML)
        vacancies = await parser.parse()

    # 2 valid posts per channel × 2 channels = 4
    assert len(vacancies) == 4
