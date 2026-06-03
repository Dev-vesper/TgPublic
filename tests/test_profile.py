from tgpublic.scraper import TelegramChannelScraper
from pathlib import Path

def download_profile_ph():
    scraper = TelegramChannelScraper("NovScript", "test_downloads")
    profile = scraper.download_profile_photo()
    assert profile.photo_url is not None, "No photo URL found"
    if profile.local_photo_path:
        assert Path(profile.local_photo_path).exists()
        print(f"✅ Profile photo downloaded to {profile.local_photo_path}")
    else:
        print("⚠️ Profile photo download failed")
    scraper.session.close()

if __name__ == "__main__":
    download_profile_ph()