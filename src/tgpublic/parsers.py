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
    attachments = _extract_attachments(widget)

    return Message(
        message_id=message_id,
        text=text,
        datetime_str=datetime_str,
        link=message_link,
        attachments=attachments,
    )


def _extract_text(widget: Tag) -> str:
    text_element = widget.find("div", class_="tgme_widget_message_text")
    if text_element:
        return text_element.get_text(strip=True)
    return ""


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