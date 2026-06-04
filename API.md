# راهنمای استفاده از TgPublic در کدهای پایتون

## نصب اولیه

```bash
git clone https://github.com/Dev-vesper/TgPublic.git
cd TgPublic
pip install -e .
```

## وارد کردن ماژول های مورد نیاز

```python
from tgpublic.scraper import TelegramChannelScraper
from tgpublic.models import Message, Attachment, ChannelProfile
```

## ایجاد یک نمونه از اسکرپر

```python
scraper = TelegramChannelScraper(channel_name="NovScript", output_dir="my_downloads")
```

channel_name بدون @ وارد میشه  
output_dir جاییه که فایل های دانلودی توش ذخیره میشن

## استفاده از context manager

برای بسته شدن خودکار session

```python
with TelegramChannelScraper("Python", "downloads") as scraper:
    messages = scraper.get_latest_messages(count=5)
    for msg in messages:
        print(msg.text)
```

## دریافت آخرین پیام ها

```python
messages = scraper.get_latest_messages(count=10)
```

خروجی لیستی از آبجکت های Message هست

هر Message این فیلدها رو داره

- message_id : str یا None
- text : str
- datetime_str : str یا None (فرمت ISO)
- link : str یا None
- views : int یا None (تعداد بازدید)
- attachments : لیستی از Attachment

## کار با attachments

```python
for msg in messages:
    for att in msg.attachments:
        print(att.type)      # image, video, document
        print(att.url)       # لینک دانلود
        print(att.filename)  # نام فایل
```

## دانلود فایل های پیوست

```python
scraper.download_message_files(messages)
```

بعد از این کار فیلد local_path در هر Attachment پر میشه (Path یا None)

اگه میخوای فقط یک فایل خاص رو دانلود کنی

```python
from tgpublic.downloader import FileDownloader

downloader = FileDownloader()
path = downloader.download(att.url, "downloads", filename=att.filename)
```

## دریافت اطلاعات پروفایل کانال

```python
profile = scraper.get_profile()
print(profile.channel_name)
print(profile.photo_url)   # آدرس عکس پروفایل
```

## دانلود عکس پروفایل

```python
profile = scraper.download_profile_photo()
print(profile.local_photo_path)   # مسیر ذخیره شده
```

اگه عکس نباشه profile.photo_url مقدار None داره

## دریافت تعداد اعضا

```python
member_count = scraper.get_member_count()
print(member_count)   # مثلاً 1245
```

این متد یک درخواست جداگانه به t.me/channel میزنه  
اگه نتونه پیدا کنه None برمیگردونه

## خروجی JSON

خودت میتونی با dataclasses.asdict تبدیل کنی

```python
from dataclasses import asdict
import json

messages = scraper.get_latest_messages(count=5)
data = [asdict(msg) for msg in messages]
json_str = json.dumps(data, indent=2, ensure_ascii=False)
```

## دسترسی به session برای درخواست های سفارشی

```python
response = scraper.session.get("https://t.me/s/NovScript")
```

بعد از کار حتماً session رو ببند

```python
scraper.session.close()
```

یا از context manager استفاده کن

## مدیریت خطاها

```python
try:
    messages = scraper.get_latest_messages(count=5)
except requests.RequestException as e:
    print("مشکل در درخواست", e)
```

خطاهای دانلود داخل خود متد download هندل میشن و لاگ میخورن  
برای گرفتن لاگ ها

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## یک مثال کامل

```python
from tgpublic.scraper import TelegramChannelScraper
from dataclasses import asdict
import json

def scrape_channel(channel_name, num_messages=3):
    with TelegramChannelScraper(channel_name, "output") as scraper:
        # دریافت پیام ها
        messages = scraper.get_latest_messages(count=num_messages)
        
        # دانلود فایل های پیوست
        scraper.download_message_files(messages)
        
        # دریافت عکس پروفایل
        profile = scraper.download_profile_photo()
        
        # دریافت تعداد اعضا
        members = scraper.get_member_count()
        
        # ساخت خروجی
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

## نکات اضافه

- فایل views به صورت خودکار از span با کلاس tgme_widget_message_views استخراج میشه و عدد K و M رو هم تبدیل میکنه (مثلاً 5.62K میشه 5620)
- متد display_messages صرفاً برای چاپ در کنسوله و در کدهای خودت معمولاً از خود مدل استفاده میکنی
- اگه به downloader نیاز داری میتونی یه نمونه جدید بسازی یا از scraper.downloader استفاده کنی
- timeout درخواست ها در config.py هست (پیش فرض 15 ثانیه)
- برای کانال های خصوصی یا حذف شده scrape کار نمیکنه
- تعداد پیام های موجود در صفحه اول t.me/s حدود 20 تا 30 تاست (همون چیزی که تلگرام نشون میده) پس با count بالاتر از اون فایده نداره

## لینک های مفید

- مخزن پروژه: [github.com/Dev-vesper/TgPublic](https://github.com/Dev-vesper/TgPublic)
- گزارش باگ یا درخواست قابلیت جدید: Issues