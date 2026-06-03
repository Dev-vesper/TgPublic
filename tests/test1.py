from tgpublic.scraper import TelegramChannelScraper
from tgpublic.models import Message

# ایجاد scraper برای یک کانال خاص
with TelegramChannelScraper("Python", "downloads") as scraper:
    messages = scraper.get_latest_messages(count=3)
    for msg in messages:
        print(msg.text)

# دریافت آخرین پیام‌ها (پیش‌فرض 2 عدد)
messages = scraper.get_latest_messages(count=5)

# چاپ متن پیام‌ها
for msg in messages:
    print(f"Message ID: {msg.message_id}")
    print(f"Text: {msg.text}")
    print(f"Date: {msg.datetime_str}")
    print(f"Link: {msg.link}")
    print(f"Attachments: {len(msg.attachments)}\n\n")

# دریافت اطلاعات پروفایل کانال
profile = scraper.get_profile()
print(f"Channel: {profile.channel_name}")
print(f"Photo URL: {profile.photo_url}")

# دانلود عکس پروفایل
profile_with_photo = scraper.download_profile_photo()
if profile_with_photo.local_photo_path:
    print(f"Profile photo saved to: {profile_with_photo.local_photo_path}")

# دانلود فایل‌های پیوست (برای همه پیام‌های قبلی)
scraper.download_message_files(messages)