import argparse
import json
import logging
import sys
from dataclasses import asdict

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from tgpublic.config import DEFAULT_DOWNLOAD_DIR, DEFAULT_MESSAGE_COUNT, ERROR_LOG_FILE
from tgpublic.display import show_banner, print_error, generate_error_code
from tgpublic.logging_config import setup_logging, setup_error_logging
from tgpublic.scraper import TelegramChannelScraper


def main():
    setup_logging()
    setup_error_logging(ERROR_LOG_FILE)

    show_banner()

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

    try:
        scraper = TelegramChannelScraper(channel_name=args.channel, output_dir=args.output)

        profile = None
        if args.download_profile:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                task = progress.add_task("[cyan]Downloading profile photo...", total=None)
                profile = scraper.download_profile_photo(
                    progress_callback=lambda d, t: progress.update(task, completed=d, total=t)
                )

        messages = scraper.get_latest_messages(count=args.num_messages)

        if args.download:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:
                for msg in messages:
                    for att in msg.attachments:
                        task = progress.add_task(
                            f"[cyan]Downloading {att.filename}", total=None
                        )
                        scraper.downloader.download(
                            att.url,
                            scraper.output_dir,
                            filename=att.filename,
                            progress_callback=lambda d, t, task=task: progress.update(
                                task, completed=d, total=t
                            ),
                        )

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

    except Exception as e:
        error_code = generate_error_code()
        logging.getLogger("tgpublic").exception(
            "Unhandled exception (code: %s)", error_code
        )
        print_error(
            f"خطای غیرمنتظره. برای جزئیات به فایل {ERROR_LOG_FILE} مراجعه کنید.",
            error_code,
        )
        sys.exit(1)


def _silence_console_logging():
    logger = logging.getLogger("tgpublic")
    logger.handlers.clear()
    logger.addHandler(logging.StreamHandler(sys.stderr))
    logger.setLevel(logging.WARNING)


if __name__ == "__main__":
    main()