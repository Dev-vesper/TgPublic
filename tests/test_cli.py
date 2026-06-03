import argparse
import logging
import sys
import tempfile
from unittest.mock import MagicMock, patch

from tgpublic import cli
from tgpublic.models import ChannelProfile, Message


def test_silence_console_logging_removes_stdout_handlers_only():
    logger = logging.getLogger("tgpublic_test_silence")
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    
    with tempfile.NamedTemporaryFile() as tmp:
        file_handler = logging.FileHandler(tmp.name)
        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)
        logger.addHandler(file_handler)

        with patch("tgpublic.cli.logging.getLogger", return_value=logger):
            cli._silence_console_logging()

        remaining_handlers = logger.handlers
        assert stdout_handler not in remaining_handlers
        assert stderr_handler in remaining_handlers
        assert file_handler in remaining_handlers
    
    logger.handlers.clear()


@patch("tgpublic.cli.TelegramChannelScraper")
def test_main_json_mode_no_progress_bars(MockScraper, capsys):
    mock_scraper = MagicMock()
    MockScraper.return_value = mock_scraper
    
    real_profile = ChannelProfile(channel_name="testchan", photo_url=None)
    mock_scraper.get_profile.return_value = real_profile
    mock_scraper.get_latest_messages.return_value = []
    mock_scraper.downloader.download.return_value = None

    test_args = ["prog", "testchan", "--json", "--download-profile", "--download"]
    with patch.object(sys, "argv", test_args):
        with patch("builtins.print") as mock_print:
            cli.main()
    
    mock_scraper.downloader.download.assert_not_called()
    captured = capsys.readouterr()
    assert "Progress" not in captured.out


@patch("tgpublic.cli.TelegramChannelScraper")
def test_main_profile_without_photo_skips_progress(MockScraper):
    mock_scraper = MagicMock()
    MockScraper.return_value = mock_scraper
    real_profile = ChannelProfile(channel_name="testchan", photo_url=None)
    mock_scraper.get_profile.return_value = real_profile

    test_args = ["prog", "testchan", "--download-profile"]
    with patch.object(sys, "argv", test_args):
        with patch("tgpublic.cli.Progress") as MockProgress:
            cli.main()
            MockProgress.assert_not_called()
    
    mock_scraper.download_profile_photo.assert_not_called()