from bs4 import BeautifulSoup

from tgpublic.parsers import parse_messages, parse_profile_photo_url


SAMPLE_HTML = """
<html>
<head>
    <meta property="og:image" content="https://cdn.telegram.org/channel_photo.jpg" />
</head>
<body>
    <div class="tgme_widget_message">
        <div class="tgme_widget_message_text">سلام دنیا</div>
        <a class="tgme_widget_message_date" href="/testchannel/12345">
            <time datetime="2025-01-01T12:00:00+00:00">Jan 1</time>
        </a>
        <img src="/file/photo_1.jpg" alt="عکس اول" />
    </div>
    <div class="tgme_widget_message">
        <div class="tgme_widget_message_text">پیام دوم</div>
        <a class="tgme_widget_message_date" href="/testchannel/12346">
            <time datetime="2025-01-02T15:30:00+00:00">Jan 2</time>
        </a>
    </div>
</body>
</html>
"""


def test_parse_profile_photo_url_from_meta():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    url = parse_profile_photo_url(soup)
    assert url == "https://cdn.telegram.org/channel_photo.jpg"


def test_parse_profile_photo_url_fallback_to_img():
    html = '<html><body><img class="tgme_page_photo_image" src="/avatar.jpg" /></body></html>'
    soup = BeautifulSoup(html, "lxml")
    url = parse_profile_photo_url(soup)
    assert url == "/avatar.jpg"


def test_parse_profile_photo_url_none():
    soup = BeautifulSoup("<html></html>", "lxml")
    url = parse_profile_photo_url(soup)
    assert url is None


def test_parse_messages_count():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    messages = parse_messages(soup, count=1)
    assert len(messages) == 1
    assert messages[0].text == "پیام دوم"


def test_parse_messages_all():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    messages = parse_messages(soup, count=10)
    assert len(messages) == 2


def test_parse_message_fields():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    messages = parse_messages(soup, count=2)
    first_message = messages[0]
    assert first_message.text == "سلام دنیا"
    assert first_message.message_id == "12345"
    assert first_message.link == "https://t.me/testchannel/12345"
    assert first_message.datetime_str == "2025-01-01T12:00:00+00:00"
    assert len(first_message.attachments) == 1
    assert first_message.attachments[0].type == "image"
    assert first_message.attachments[0].filename == "عکس اول"


def test_parse_messages_empty():
    soup = BeautifulSoup("<html></html>", "lxml")
    messages = parse_messages(soup, count=2)
    assert messages == []


def test_parse_messages_with_zero_count_returns_one_message():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    messages = parse_messages(soup, count=0)
    assert len(messages) == 1
    assert messages[0].text == "پیام دوم"


def test_parse_messages_with_negative_count_returns_one_message():
    soup = BeautifulSoup(SAMPLE_HTML, "lxml")
    messages = parse_messages(soup, count=-5)
    assert len(messages) == 1
    assert messages[0].text == "پیام دوم"