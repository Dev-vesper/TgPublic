from tgpublic.scraper import TelegramChannelScraper

def fetch_messages():
    scraper = TelegramChannelScraper("NovScript", "test_downloads")
    messages = scraper.get_latest_messages(count=2)
    assert len(messages) > 0, "No messages fetched"
    assert messages[0].text is not None
    print("✅ Test passed: messages fetched successfully")
    scraper.session.close()

if __name__ == "__main__":
    fetch_messages()