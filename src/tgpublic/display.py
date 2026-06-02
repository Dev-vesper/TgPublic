import random
import string

from big_text import big_text
from rich.console import Console
from rich.text import Text

console = Console()


def show_banner():
    banner = big_text("TgPublic")
    console.print(banner, style="bold cyan")


def print_error(message: str, code: str):
    error_text = Text()
    error_text.append("ERROR", style="bold white on #ff69b4")
    error_text.append(f" [{code}] {message}", style="bold #ff69b4")
    console.print(error_text)


def generate_error_code() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))