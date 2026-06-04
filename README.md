# TgPublic

ابزار خط فرمان برای استخراج داده از کانال‌های عمومی تلگرام (بدون نیاز به API رسمی).  
با TgPublic می‌توانید:

- دریافت آخرین پیام‌های یک کانال عمومی به همراه متن، زمان، لینک و تعداد بازدید
- دانلود خودکار تمام پیوست‌ها (تصویر، ویدیو، سند)
- دریافت آدرس و دانلود عکس پروفایل کانال
- مشاهده تعداد اعضای کانال (از صفحه اصلی تلگرام)
- خروجی JSON برای پردازش در دیگر ابزارها

---

## نصب

### پیش‌نیازها
- Python 3.9 یا بالاتر
- pip

### نصب از روی مخزن (برای آخرین تغییرات)
```bash
git clone https://github.com/Dev-vesper/TgPublic.git
cd TgPublic
pip install -e .
```

### نصب با وابستگی‌های توسعه (برای اجرای تست)
```bash
pip install -e ".[dev]"
```

---

## راهنمای استفاده سریع

```bash
tgpublic CHANNEL_NAME [OPTIONS]
```

- `CHANNEL_NAME`: نام کانال بدون `@` (مثال: `NovScript`)

### دریافت ۵ پیام آخر
```bash
tgpublic NovScript -n 5
```

### دریافت پیام‌ها به همراه دانلود فایل‌های پیوست
```bash
tgpublic NovScript -n 3 --download
```

### دریافت عکس پروفایل کانال
```bash
tgpublic NovScript --download-profile
```

### مشاهده تعداد اعضا (همراه با پیام‌ها)
```bash
tgpublic NovScript --members
```

### فقط دریافت تعداد اعضا (بدون پیام و دانلود)
```bash
tgpublic NovScript --only_members
```

### دریافت خروجی JSON (برای پردازش با اسکریپت)
```bash
tgpublic NovScript -n 10 --json
```

### ترکیب چند گزینه
```bash
tgpublic NovScript -n 5 --download --download-profile --members -o my_downloads
```

---

## توضیح کامل گزینه‌ها

| گزینه | توضیح |
|-------|-------|
| `channel` | نام کانال تلگرام (بدون `@`). اگر وارد نشود، برنامه از شما می‌پرسد. |
| `-n`, `--num-messages` | تعداد آخرین پیام‌های مورد نظر (پیش‌فرض: ۲). |
| `-d`, `--download` | دانلود تمام فایل‌های پیوست پیام‌ها (تصاویر، ویدیوها، اسناد). |
| `--download-profile` | دانلود عکس پروفایل کانال و ذخیره با نام `{channel}_profile.jpg`. |
| `--members` | نمایش تعداد اعضای کانال (نیاز به یک درخواست جداگانه به `t.me/{channel}` دارد). |
| `--only_members` | فقط تعداد اعضا را دریافت کند و هیچ پیام یا دانلودی انجام ندهد. |
| `-o`, `--output` | مسیر پوشه ذخیره فایل‌های دانلودی (پیش‌فرض: `downloads/`). |
| `--json` | خروجی را به صورت JSON خام چاپ کند (مناسب برای پردازش خودکار). |
| `-h`, `--help` | نمایش راهنما. |

---

## خروجی نمونه

### حالت عادی (بدون `--json`)
```
████████╗  ██████╗  ██████╗  ██╗   ██╗ ██████╗  ██╗      ██╗  ██████╗
╚══██╔══╝ ██╔════╝  ██╔══██╗ ██║   ██║ ██╔══██╗ ██║      ██║ ██╔════╝
   ██║    ██║  ███╗ ██████╔╝ ██║   ██║ ██████╔╝ ██║      ██║ ██║
   ██║    ██║   ██║ ██╔═══╝  ██║   ██║ ██╔══██╗ ██║      ██║ ██║
   ██║    ╚██████╔╝ ██║      ╚██████╔╝ ██████╔╝ ███████╗ ██║ ╚██████╗
   ╚═╝     ╚═════╝  ╚═╝       ╚═════╝  ╚═════╝  ╚══════╝ ╚═╝  ╚═════╝

👥 تعداد اعضای کانال @NovScript: 32

============================================================
📨 پیام 1
شناسه: 154
زمان: 2026-05-27 20:44:02
👁️ بازدیدها: 1,234
متن:
ماشالا سطح برنامه نویسامون انقدر رفته بالا که هرجور پروژه به ذهنم میاد یکی 10 لول بهترش رو پابلیک کرده گیتهاب
لینک: https://t.me/NovScript/154
📎 پیوست‌ها (1 عدد):
   ✅ DZdcjLQDv_guPZzsH_fn1_XJZmB9yUDQuYvCmJg1HOiVuN-yfRtOHjIBkPc3sxCvPYL4gSMI8LydPwCneEi9JgAyA8cuMy4aTdK7SHt91lSwEJD7jTSuxH6JDEcUUfTMG1TGtdejY-F6JIriC3aWOFLYF46T4rhdNmscatoQ0UkzMfvBug5nkx6-wyA2nQzG3CLu36ZZ1RdHhw26haahAil75xAUw9phonnki6Kd6rq8U9ARc5KggDLbR0HKuy4-ZQ7nhveX0gzfJQ5s8wnp3adAQJHdB3nBq8t372CC4kyaI-6bsrs5D3OL9QvC0HOMAR-HG-D3JzgBpB1ZhNcs4Q.jpg (image)
      مسیر: downloads\DZdcjLQDv_guPZzsH_fn1_XJZmB9yUDQuYvCmJg1HOiVuN-yfRtOHjIBkPc3sxCvPYL4gSMI8LydPwCneEi9JgAyA8cuMy4aTdK7SHt91lSwEJD7jTSuxH6JDEcUUfTMG1TGtdejY-F6JIriC3aWOFLYF46T4rhdNmscatoQ0UkzMfvBug5nkx6-wyA2nQzG3CLu36ZZ1RdHhw26haahAil75xAUw9phonnki6Kd6rq8U9ARc5KggDLbR0HKuy4-ZQ7nhveX0gzfJQ5s8wnp3adAQJHdB3nBq8t372CC4kyaI-6bsrs5D3OL9QvC0HOMAR-HG-D3JzgBpB1ZhNcs4Q.jpg
...
```

### حالت JSON
```bash
tgpublic NovScript --only_members --json
```
خروجی:
```json
{
  "profile": {
    "member_count": 32
  }
}
```

---

## لاگ‌ها و خطاها

- تمام لاگ‌ها با سطح `INFO` در کنسول نمایش داده می‌شوند.
- خطاهای جدی در فایل `tgpublic_errors.log` ذخیره می‌شوند (حداکثر ۵ مگابایت، ۳ نسخه چرخشی).
- اگر خطای غیرمنتظره رخ دهد، یک کد ۶ رقمی نمایش داده می‌شود که می‌توانید برای عیب‌یابی از فایل خطا استفاده کنید.

---

## توسعه و مشارکت

### اجرای تست‌ها
```bash
pytest
```

### ساختار پروژه
```
tgpublic/
├── src/tgpublic/
│   ├── cli.py           # نقطه ورود خط فرمان
│   ├── scraper.py       # کلاس اصلی استخراج‌کننده
│   ├── parsers.py       # پارسینگ HTML با BeautifulSoup
│   ├── downloader.py    # دانلود فایل با قابلیت resume (جزئی)
│   ├── models.py        # مدل‌های داده (Message, Attachment, ...)
│   ├── config.py        # ثابت‌ها (URLها، timeout, ...)
│   ├── logging_config.py # پیکربندی لاگ
│   └── display.py       # نمایش بنر و خطاهای رنگی
├── py_tests/            # تست‌های واحد (با pytest)
├── tests/               # اسکریپت‌های تست دستی (اختیاری)
└── pyproject.toml       # تنظیمات پروژه و وابستگی‌ها
```

### افزودن قابلیت جدید
1. در صورت نیاز، مدل را در `models.py` به‌روزرسانی کنید.
2. تابع پارسینگ را در `parsers.py` بنویسید.
3. متد مربوطه را به `TelegramChannelScraper` اضافه کنید.
4. گزینه خط فرمان را در `cli.py` تعریف کنید.
5. تست واحد بنویسید و با `pytest` تأیید کنید.

---

## مجوز

این پروژه تحت مجوز **MIT** منتشر شده است (فایل `LICENSE` را ببینید).

---

## تماس و مشارکت

- توسعه‌دهنده: [Dev-vesper](https://github.com/Dev-vesper)
- برای گزارش مشکل یا پیشنهاد، یک **Issue** در مخزن گیت‌هاب باز کنید.
- مشارکت از طریق Pull Request با استقبال روبرو می‌شود.

---

**TgPublic** – استخراج ساده و سریع از کانال‌های عمومی تلگرام، بدون نیاز به API و احراز هویت.