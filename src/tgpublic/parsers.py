import re
import urllib.parse
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag

from tgpublic.models import Attachment, Message


def parse_profile_photo_url(soup: BeautifulSoup) -> Optional[str]:
    meta_tag = soup.find("meta", property="og:image")
    if meta_tag and meta_tag.get("content"):
        return meta_tag["content"]

    img_tag = soup.find("img", class_="tgme_page_photo_image")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    return None


def parse_member_count(soup: BeautifulSoup) -> Optional[int]:
    extra_div = soup.find("div", class_="tgme_page_extra")
    if not extra_div:
        return None

    text = extra_div.get_text(strip=True)
    match = re.search(r"([\d,]+)\s*(?:member|subscriber|عضو|members|subscribers)", text, re.IGNORECASE)
    if match:
        cleaned = match.group(1).replace(",", "")
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def parse_messages(soup: BeautifulSoup, count: int) -> list[Message]:
    message_widgets = soup.find_all("div", class_="tgme_widget_message")
    if not message_widgets:
        return []

    effective_count = max(1, min(count, len(message_widgets)))
    target_widgets = message_widgets[-effective_count:]
    messages = []

    for widget in target_widgets:
        message = _parse_single_message(widget)
        messages.append(message)

    return messages


def _parse_single_message(widget: Tag) -> Message:
    text = _extract_text(widget)
    message_id, message_link = _extract_id_and_link(widget)
    datetime_str = _extract_datetime(widget)
    views = _extract_views_count(widget)
    attachments = _extract_attachments(widget)

    return Message(
        message_id=message_id,
        text=text,
        datetime_str=datetime_str,
        link=message_link,
        views=views,
        attachments=attachments,
    )


def _extract_text(widget: Tag) -> str:
    text_element = widget.find("div", class_="tgme_widget_message_text")
    if not text_element:
        return ""

    def _extract_inner(element):
        parts = []
        for child in element.children:
            if isinstance(child, str):
                collapsed = re.sub(r'[ \t]+', ' ', child)
                parts.append(collapsed)
            elif child.name == 'br':
                parts.append('\n')
            elif child.name in ['a', 'span', 'strong', 'em']:
                parts.append(_extract_inner(child))
            else:
                parts.append(_extract_inner(child))
        return ''.join(parts)

    raw_text = _extract_inner(text_element)
    lines = [line.strip() for line in raw_text.split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def _extract_id_and_link(widget: Tag) -> tuple[Optional[str], Optional[str]]:
    link_element = widget.find("a", class_="tgme_widget_message_date")
    if not link_element or not link_element.has_attr("href"):
        return None, None

    href = link_element["href"]
    full_link = href if href.startswith("http") else f"https://t.me{href}"
    match = re.search(r"/(\d+)$", full_link)
    message_id = match.group(1) if match else None

    return message_id, full_link


def _extract_datetime(widget: Tag) -> Optional[str]:
    time_element = widget.find("time")
    if time_element and time_element.has_attr("datetime"):
        return time_element["datetime"]
    return None


def _extract_views_count(widget: Tag) -> Optional[int]:
    if widget.name == 'span' and 'tgme_widget_message_views' in widget.get('class', []):
        views_span = widget
    else:
        views_span = widget.find("span", class_="tgme_widget_message_views")
    
    if not views_span:
        return None
    
    text = views_span.get_text(strip=True)
    text_upper = text.upper()
    multiplier = 1
    
    if text_upper.endswith('K'):
        multiplier = 1000
        text = text_upper[:-1]
    elif text_upper.endswith('M'):
        multiplier = 1000000
        text = text_upper[:-1]
    
    try:
        if '.' in text:
            value = float(text)
        else:
            value = int(text)
        return int(value * multiplier)
    except ValueError:
        return None


def _extract_attachments(widget: Tag) -> list[Attachment]:
    attachments = []
    seen_urls: set[str] = set()

    for processor in [
        _find_image_attachments,
        _find_video_attachments,
        _find_document_links,
        _find_background_images,
    ]:
        for attachment in processor(widget):
            if attachment.url not in seen_urls:
                seen_urls.add(attachment.url)
                attachments.append(attachment)

    return attachments


def _find_image_attachments(widget: Tag) -> list[Attachment]:
    attachments = []
    for img in widget.find_all("img"):
        if not img.has_attr("src"):
            continue
        url = _normalize_url(img["src"])
        if url.startswith("data:"):
            continue
        filename = _extract_image_filename(img, len(attachments))
        attachments.append(Attachment(type="image", url=url, filename=filename))
    return attachments


def _find_video_attachments(widget: Tag) -> list[Attachment]:
    attachments = []
    for video in widget.find_all("video"):
        if not video.has_attr("src"):
            continue
        url = _normalize_url(video["src"])
        parsed = urllib.parse.urlparse(url)
        filename = Path(parsed.path).name or f"video_{len(attachments)}.mp4"
        attachments.append(Attachment(type="video", url=url, filename=filename))
    return attachments


def _find_document_links(widget: Tag) -> list[Attachment]:
    attachments = []
    for link in widget.find_all("a", class_="tgme_widget_message_document_wrap"):
        if not link.has_attr("href"):
            continue
        url = _normalize_url(link["href"])
        filename_element = link.find("span", class_="tgme_widget_message_document_title")
        filename = filename_element.get_text(strip=True) if filename_element else "document.bin"
        attachments.append(Attachment(type="document", url=url, filename=filename))
    return attachments


def _find_background_images(widget: Tag) -> list[Attachment]:
    attachments = []
    for element in widget.find_all(style=True):
        style = element.get("style", "")
        match = re.search(r"background-image:\s*url\(['\"]?([^'\"]+)['\"]?\)", style)
        if match:
            url = _normalize_url(match.group(1))
            filename = f"background_{len(attachments)}.jpg"
            attachments.append(Attachment(type="image", url=url, filename=filename))
    return attachments


def _normalize_url(url: str) -> str:
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith("/"):
        return f"https://t.me{url}"
    return url


def _extract_image_filename(img: Tag, index: int) -> str:
    if img.has_attr("alt") and img["alt"]:
        safe_name = re.sub(r'[<>:"/\\|?*]', "_", img["alt"][:50])
        if safe_name:
            return safe_name
    parsed = urllib.parse.urlparse(img["src"])
    name = Path(parsed.path).name
    return name or f"image_{index}.jpg"