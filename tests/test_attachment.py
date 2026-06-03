from tgpublic.scraper import TelegramChannelScraper
from pathlib import Path

def download_attachments():
    scraper = TelegramChannelScraper("NovScript", "test_downloads")
    messages = scraper.get_latest_messages(count=5)
    scraper.download_message_files(messages)
    for msg in messages:
        for att in msg.attachments:
            if att.local_path:
                assert Path(att.local_path).exists()
                print(f"✅ Downloaded: {att.filename} -> {att.local_path}")
            else:
                print(f"⚠️ Failed: {att.filename}")
    scraper.session.close()

if __name__ == "__main__":
    download_attachments()