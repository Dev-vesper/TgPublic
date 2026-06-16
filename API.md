# Guide for Using TgPublic in Python Code

## Initial Installation

```bash
git clone https://github.com/Dev-vesper/TgPublic.git
cd TgPublic
pip install -e .
```

## Importing Required Modules

```python
from tgpublic.scraper import TelegramChannelScraper
from tgpublic.models import Message, Attachment, ChannelProfile
```

## Creating a Scraper Instance

```python
scraper = TelegramChannelScraper(channel_name="NovScript", output_dir="my_downloads")
```

- `channel_name` is entered without the `@`
- `output_dir` is where downloaded files will be saved

## Using a Context Manager

For automatic session closure:

```python
with TelegramChannelScraper("Python", "downloads") as scraper:
    messages = scraper.get_latest_messages(count=5)
    for msg in messages:
        print(msg.text)
```

## Retrieving Latest Messages

```python
messages = scraper.get_latest_messages(count=10)
```

Output is a list of `Message` objects.

Each `Message` has the following fields:

- `message_id`: str or None
- `text`: str
- `datetime_str`: str or None (ISO format)
- `link`: str or None
- `views`: int or None (view count)
- `attachments`: list of `Attachment`

## Working with Attachments

```python
for msg in messages:
    for att in msg.attachments:
        print(att.type)      # image, video, document
        print(att.url)       # download link
        print(att.filename)  # file name
```

## Downloading Attachments

```python
scraper.download_message_files(messages)
```

After this, the `local_path` field in each `Attachment` will be populated (Path or None).

If you want to download only a specific file:

```python
from tgpublic.downloader import FileDownloader

downloader = FileDownloader()
path = downloader.download(att.url, "downloads", filename=att.filename)
```

## Retrieving Channel Profile Information

```python
profile = scraper.get_profile()
print(profile.channel_name)
print(profile.photo_url)   # profile picture URL
```

## Downloading Profile Picture

```python
profile = scraper.download_profile_photo()
print(profile.local_photo_path)   # saved path
```

If no picture exists, `profile.photo_url` will be `None`.

## Getting Member Count

```python
member_count = scraper.get_member_count()
print(member_count)   # e.g., 1245
```

This method makes a separate request to `t.me/channel`.  
If it cannot be found, it returns `None`.

## JSON Output

You can convert using `dataclasses.asdict`:

```python
from dataclasses import asdict
import json

messages = scraper.get_latest_messages(count=5)
data = [asdict(msg) for msg in messages]
json_str = json.dumps(data, indent=2, ensure_ascii=False)
```

## Accessing the Session for Custom Requests

```python
response = scraper.session.get("https://t.me/s/NovScript")
```

Remember to close the session afterwards:

```python
scraper.session.close()
```

Or use the context manager.

## Error Handling

```python
try:
    messages = scraper.get_latest_messages(count=5)
except requests.RequestException as e:
    print("Request error:", e)
```

Download errors are handled inside the `download` method itself and are logged.  
To capture logs:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## A Complete Example

```python
from tgpublic.scraper import TelegramChannelScraper
from dataclasses import asdict
import json

def scrape_channel(channel_name, num_messages=3):
    with TelegramChannelScraper(channel_name, "output") as scraper:
        # Get messages
        messages = scraper.get_latest_messages(count=num_messages)
        
        # Download attachments
        scraper.download_message_files(messages)
        
        # Get profile picture
        profile = scraper.download_profile_photo()
        
        # Get member count
        members = scraper.get_member_count()
        
        # Build output
        result = {
            "channel": channel_name,
            "member_count": members,
            "profile_photo": str(profile.local_photo_path) if profile.local_photo_path else None,
            "messages": [
                {
                    "id": m.message_id,
                    "text": m.text,
                    "views": m.views,
                    "attachments": [
                        {"type": a.type, "filename": a.filename, "saved": str(a.local_path) if a.local_path else None}
                        for a in m.attachments
                    ]
                }
                for m in messages
            ]
        }
        
        return result

if __name__ == "__main__":
    data = scrape_channel("NovScript", 2)
    print(json.dumps(data, indent=2, ensure_ascii=False))
```

## Additional Notes

- The `views` field is automatically extracted from a `<span>` with class `tgme_widget_message_views` and handles K/M suffixes (e.g., 5.62K becomes 5620).
- The `display_messages` method is only for console printing; in your own code you typically work directly with the model objects.
- If you need a downloader, you can create a new instance or use `scraper.downloader`.
- Request timeouts are defined in `config.py` (default 15 seconds).
- Scraping does not work for private or deleted channels.
- The first page of `t.me/s` typically contains about 20–30 messages (the same as what Telegram shows), so specifying a `count` higher than that will not fetch more.

## Useful Links

- Project repository: [github.com/Dev-vesper/TgPublic](https://github.com/Dev-vesper/TgPublic)
- Bug reports or feature requests: Issues
