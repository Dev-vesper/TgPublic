import logging
from datetime import datetime, timezone
from typing import Optional, Callable

import requests
from bs4 import BeautifulSoup

from tgpublic.config import (
    DEFAULT_MESSAGE_COUNT,
    DEFAULT_REQUEST_TIMEOUT,
    TELEGRAM_VIEW_URL,
    USER_AGENT,
)
from tgpublic.downloader import FileDownloader
from tgpublic.models import ChannelProfile, Message
from tgpublic.parsers import parse_messages, parse_profile_photo_url, parse_member_count

logger = logging.getLogger("tgpublic")


class TelegramChannelScraper:
    def __init__(self, channel_name: str, output_dir: str) -> None:
        self.channel_name = channel_name
        self.page_url = f"{TELEGRAM_VIEW_URL}/{channel_name}"
        self.output_dir = output_dir
        self.downloader = FileDownloader()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def fetch_page_soup(self) -> BeautifulSoup:
        logger.info("Fetching page: %s", self.page_url)
        response = self.session.get(self.page_url, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.info("Page fetched successfully (status %d)", response.status_code)
        return BeautifulSoup(response.text, "lxml")

    def get_profile(self) -> ChannelProfile:
        soup = self.fetch_page_soup()
        photo_url = parse_profile_photo_url(soup)
        profile = ChannelProfile(channel_name=self.channel_name, photo_url=photo_url)
        logger.info("Profile parsed. Photo URL: %s", photo_url)
        return profile

    def get_member_count(self) -> Optional[int]:
        main_url = f"https://t.me/{self.channel_name}"
        logger.info("Fetching member count from: %s", main_url)
        try:
            response = self.session.get(main_url, timeout=DEFAULT_REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            count = parse_member_count(soup)
            if count is not None:
                logger.info("Member count for @%s: %d", self.channel_name, count)
            else:
                logger.warning("Could not find member count for @%s", self.channel_name)
            return count
        except requests.RequestException as e:
            logger.error("Failed to fetch member count for @%s: %s", self.channel_name, e)
            return None

    def download_profile_photo(
        self,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> ChannelProfile:
        profile = self.get_profile()
        if not profile.photo_url:
            logger.warning("No profile photo URL found for channel @%s", self.channel_name)
            return profile
        logger.info("Downloading profile photo...")
        local_path = self.downloader.download(
            profile.photo_url,
            self.output_dir,
            filename=f"{self.channel_name}_profile.jpg",
            progress_callback=progress_callback,
        )
        profile.local_photo_path = local_path
        if local_path:
            logger.info("Profile photo saved to %s", local_path)
        else:
            logger.error("Failed to download profile photo")
        return profile

    def get_latest_messages(self, count: int = DEFAULT_MESSAGE_COUNT) -> list[Message]:
        soup = self.fetch_page_soup()
        messages = parse_messages(soup, count)
        logger.info("Parsed %d messages", len(messages))
        return messages

    def download_message_files(
        self,
        messages: list[Message],
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> list[Message]:
        logger.info("Starting download of attachments for %d messages", len(messages))
        for message in messages:
            for attachment in message.attachments:
                logger.info("Downloading attachment: %s", attachment.filename)
                local_path = self.downloader.download(
                    attachment.url,
                    self.output_dir,
                    filename=attachment.filename,
                    progress_callback=progress_callback,
                )
                attachment.local_path = local_path
                if local_path:
                    logger.info("Attachment saved to %s", local_path)
                else:
                    logger.error("Failed to download attachment: %s", attachment.url)
        return messages

    def display_messages(self, messages: list[Message]) -> None:
        for idx, message in enumerate(messages, 1):
            print(f"\n{'='*60}")
            print(f"📨 پیام {idx}")
            if message.message_id:
                print(f"شناسه: {message.message_id}")
            if message.datetime_str:
                try:
                    dt = datetime.fromisoformat(message.datetime_str.replace("Z", "+00:00"))
                    dt_local = dt.astimezone()
                    print(f"زمان: {dt_local.strftime('%Y-%m-%d %H:%M:%S')}")
                except ValueError:
                    print(f"زمان: {message.datetime_str}")
            if message.views is not None:
                print(f"👁️ بازدیدها: {message.views:,}")
            print(f"متن:\n{message.text or '[بدون متن]'}")
            if message.link:
                print(f"لینک: {message.link}")
            if message.attachments:
                print(f"📎 پیوست‌ها ({len(message.attachments)} عدد):")
                for att in message.attachments:
                    status = "✅" if att.local_path else "⏳"
                    print(f"   {status} {att.filename} ({att.type})")
                    if att.local_path:
                        print(f"      مسیر: {att.local_path}")