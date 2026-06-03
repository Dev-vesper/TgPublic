from tgpublic.scraper import TelegramChannelScraper

def preserve_newlines():
    scraper = TelegramChannelScraper("NovScript", "test_downloads")
    messages = scraper.get_latest_messages(count=4)
    found = False
    for msg in messages:
        if '\n' in msg.text:
            print(f"✅ Found newline in message {msg.message_id}:")
            print(repr(msg.text))
            found = True
            break
    if not found:
        print("⚠️ No newline found in recent messages (maybe no multi-line messages)")
    scraper.session.close()

if __name__ == "__main__":
    preserve_newlines()