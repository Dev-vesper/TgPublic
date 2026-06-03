from tgpublic.scraper import TelegramChannelScraper
from dataclasses import asdict
import json

def serialization():
    scraper = TelegramChannelScraper("NovScript", "test_downloads")
    messages = scraper.get_latest_messages(count=2)
    data = [asdict(msg) for msg in messages]
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    assert isinstance(json_str, str)
    print("✅ JSON serialization successful")
    print(json_str[:500] + "...")  # پرینت کردن 500 کاراکتر اول
    scraper.session.close()

if __name__ == "__main__":
    serialization()