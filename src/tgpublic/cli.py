import argparse
import json
import logging
import sys
from dataclasses import asdict

from tgpublic.config import DEFAULT_DOWNLOAD_DIR, DEFAULT_MESSAGE_COUNT
from tgpublic.logging_config import setup_logging
from tgpublic.scraper import TelegramChannelScraper


def main():
    setup_logging()

    parser = argparse.ArgumentParser(
        prog="tgpublic",
        description="دانلود پیام‌ها، فایل‌ها و عکس پروفایل از کانال‌های عمومی تلگرام",
    )
    parser.add_argument(
        "channel",
        nargs="?",
        help="نام کانال تلگرام (بدون @)",
    )
    parser.add_argument(
        "-n",
        "--num-messages",
        type=int,
        default=DEFAULT_MESSAGE_COUNT,
        help=f"تعداد آخرین پیام‌ها برای دریافت (پیش‌فرض: {DEFAULT_MESSAGE_COUNT})",
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="دانلود فایل‌های پیوست پیام‌ها",
    )
    parser.add_argument(
        "--download-profile",
        action="store_true",
        help="دانلود عکس پروفایل کانال",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_DOWNLOAD_DIR,
        help=f"پوشه خروجی برای فایل‌های دانلودی (پیش‌فرض: {DEFAULT_DOWNLOAD_DIR})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="خروجی به صورت JSON خام",
    )

    args = parser.parse_args()

    if not args.channel:
        args.channel = input("لطفاً نام کانال را وارد کنید (بدون @): ").strip()
        if not args.channel:
            print("❌ نام کانال الزامی است.")
            sys.exit(1)

    if args.json:
        _silence_console_logging()

    scraper = TelegramChannelScraper(channel_name=args.channel, output_dir=args.output)

    profile = None
    if args.download_profile:
        profile = scraper.download_profile_photo()

    messages = scraper.get_latest_messages(count=args.num_messages)

    if args.download:
        scraper.download_message_files(messages)

    if args.json:
        output_data = {"messages": [asdict(msg) for msg in messages]}
        if profile:
            output_data["profile"] = asdict(profile)

        print(json.dumps(output_data, indent=2, ensure_ascii=False, default=str))
        return

    if profile:
        print(f"\n🖼️ عکس پروفایل کانال @{args.channel}:")
        if profile.local_photo_path:
            print(f"   ✅ دانلود شد: {profile.local_photo_path}")
        elif profile.photo_url:
            print(f"   ⚠️ آدرس پیدا شد اما دانلود ناموفق بود: {profile.photo_url}")
        else:
            print("   ❌ عکس پروفایلی یافت نشد.")

    scraper.display_messages(messages)


def _silence_console_logging():
    logger = logging.getLogger("tgpublic")
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.WARNING)


if __name__ == "__main__":
    main()