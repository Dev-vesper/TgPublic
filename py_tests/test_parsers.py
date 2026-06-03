from bs4 import BeautifulSoup

from tgpublic.parsers import parse_messages, parse_profile_photo_url, parse_member_count, _extract_views_count


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

HTML_WITH_NEWLINE = """
<html>
<body>
    <div class="tgme_widget_message">
        <div class="tgme_widget_message_text">خط اول\nخط دوم\n  خط سوم با فاصله  اضافی</div>
        <a class="tgme_widget_message_date" href="/testchannel/12347"><time datetime="2025-01-03T10:00:00+00:00"/></a>
    </div>
</body>
</html>
"""

HTML_WITH_BR_TAGS = """
<html>
<body>
    <div class="tgme_widget_message">
        <div class="tgme_widget_message_text">
            ایران عالیه<br/>نصب کنید
        </div>
        <a class="tgme_widget_message_date" href="/test/1"><time datetime="2025-01-01"/></a>
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


def test_parse_message_preserves_newlines():
    soup = BeautifulSoup(HTML_WITH_NEWLINE, "lxml")
    messages = parse_messages(soup, count=1)
    assert len(messages) == 1
    expected = "خط اول\nخط دوم\nخط سوم با فاصله اضافی"
    assert messages[0].text == expected

def test_parse_message_with_br_tags():
    soup = BeautifulSoup(HTML_WITH_BR_TAGS, "lxml")
    messages = parse_messages(soup, count=1)
    assert len(messages) == 1
    assert messages[0].text == "ایران عالیه\nنصب کنید"

def test_parse_member_count_with_subscribers():
    html = '<div class="tgme_page_extra">32 subscribers</div>'
    soup = BeautifulSoup(html, "lxml")
    assert parse_member_count(soup) == 32

def test_parse_member_count_with_members():
    html = '<div class="tgme_page_extra">1,234 members</div>'
    soup = BeautifulSoup(html, "lxml")
    assert parse_member_count(soup) == 1234

def test_parse_member_count_with_persian():
    html = '<div class="tgme_page_extra">۵۰۰ عضو</div>'
    soup = BeautifulSoup(html, "lxml")
    assert parse_member_count(soup) == 500

def test_parse_member_count_no_extra():
    soup = BeautifulSoup("<html></html>", "lxml")
    assert parse_member_count(soup) is None

def test_parse_member_count_other_text():
    html = '<div class="tgme_page_extra">Joined December 2020</div>'
    soup = BeautifulSoup(html, "lxml")
    assert parse_member_count(soup) is None

def test_extract_views_count():
    html = '<span class="tgme_widget_message_views">5.62K</span>'
    soup = BeautifulSoup(html, "lxml")
    views = _extract_views_count(soup.find("span"))
    assert views == 5620

def test_extract_views_count_simple():
    html = '<span class="tgme_widget_message_views">1234</span>'
    soup = BeautifulSoup(html, "lxml")
    views = _extract_views_count(soup.find("span"))
    assert views == 1234

def test_extract_views_count_million():
    html = '<span class="tgme_widget_message_views">1.2M</span>'
    soup = BeautifulSoup(html, "lxml")
    views = _extract_views_count(soup.find("span"))
    assert views == 1200000

def test_extract_views_count_missing():
    soup = BeautifulSoup("<div></div>", "lxml")
    views = _extract_views_count(soup)
    assert views is None