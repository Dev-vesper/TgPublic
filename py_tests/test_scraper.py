import requests
from unittest.mock import MagicMock, patch

from tgpublic.scraper import TelegramChannelScraper


SAMPLE_HTML = """
<html>
<head><meta property="og:image" content="https://cdn.telegram.org/avatar.jpg" /></head>
<body>
    <div class="tgme_widget_message">
        <div class="tgme_widget_message_text">Test message</div>
        <a class="tgme_widget_message_date" href="/test/100"><time datetime="2025-06-02T10:00:00+00:00"/></a>
        <img src="/file/img.jpg" alt="test image" />
    </div>
</body>
</html>
"""


@patch("tgpublic.scraper.requests.Session.get")
def test_get_profile(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    scraper = TelegramChannelScraper("test", "downloads")
    profile = scraper.get_profile()

    assert profile.channel_name == "test"
    assert profile.photo_url == "https://cdn.telegram.org/avatar.jpg"


@patch("tgpublic.scraper.requests.Session.get")
def test_get_latest_messages(mock_get):
    mock_response = MagicMock()
    mock_response.text = SAMPLE_HTML
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    scraper = TelegramChannelScraper("test", "downloads")
    messages = scraper.get_latest_messages(count=1)

    assert len(messages) == 1
    assert messages[0].text == "Test message"
    assert messages[0].message_id == "100"
    assert len(messages[0].attachments) == 1


def test_scraper_context_manager_closes_session():
    scraper = TelegramChannelScraper("test", "downloads")
    session = scraper.session
    with patch.object(session, "close") as mock_close:
        with scraper:
            pass
        mock_close.assert_called_once()


def test_display_messages_handles_none_datetime(capsys):
    from tgpublic.models import Message
    scraper = TelegramChannelScraper("test", "downloads")
    msg = Message(message_id="1", text="hello", datetime_str=None, link=None)
    scraper.display_messages([msg])
    captured = capsys.readouterr()
    assert "زمان: None" not in captured.out
    assert "متن:" in captured.out

@patch("tgpublic.scraper.requests.Session.get")
def test_get_member_count_success(mock_get):
    mock_response = MagicMock()
    mock_response.text = '<div class="tgme_page_extra">128 subscribers</div>'
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    scraper = TelegramChannelScraper("test", "downloads")
    count = scraper.get_member_count()
    assert count == 128
    mock_get.assert_called_once_with("https://t.me/test", timeout=15)

@patch("tgpublic.scraper.requests.Session.get")
def test_get_member_count_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    scraper = TelegramChannelScraper("test", "downloads")
    count = scraper.get_member_count()
    assert count is None

@patch("tgpublic.scraper.requests.Session.get")
def test_get_member_count_request_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("timeout")
    scraper = TelegramChannelScraper("test", "downloads")
    count = scraper.get_member_count()
    assert count is None