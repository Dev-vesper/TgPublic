from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Attachment:
    type: str
    url: str
    filename: str
    local_path: Optional[Path] = None


@dataclass
class ChannelProfile:
    channel_name: str
    photo_url: Optional[str] = None
    local_photo_path: Optional[Path] = None
    member_count: Optional[int] = None


@dataclass
class Message:
    message_id: Optional[str] = None
    text: str = ""
    datetime_str: Optional[str] = None
    link: Optional[str] = None
    attachments: list[Attachment] = field(default_factory=list)