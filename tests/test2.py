from tgpublic.scraper import TelegramChannelScraper
from dataclasses import asdict
import json

scraper = TelegramChannelScraper("NovScript", "downloads")
messages = scraper.get_latest_messages(count=2)

# تبدیل به لیست دیکشنری
messages_dict = [asdict(msg) for msg in messages]

# ذخیره در فایل JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(messages_dict, f, indent=2, ensure_ascii=False)