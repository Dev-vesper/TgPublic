# TgPublic

Command-line tool for extracting data from public Telegram channels (without requiring the official API).  
With TgPublic you can:

- Retrieve the latest messages from a public channel, including text, timestamp, link, and view count
- Automatically download all attachments (images, videos, documents)
- Get the channel profile picture URL and download it
- View the channel member count (from the Telegram main page)
- Output in JSON format for processing in other tools

---

## Installation

### Prerequisites
- Python 3.9 or higher
- pip

### Install from repository (for latest changes)
```bash
git clone https://github.com/Dev-vesper/TgPublic.git
cd TgPublic
pip install -e .
```

### Install with development dependencies (for running tests)
```bash
pip install -e ".[dev]"
```

---

## Quick Start Guide

```bash
tgpublic CHANNEL_NAME [OPTIONS]
```

- `CHANNEL_NAME`: channel name without `@` (example: `NovScript`)

### Get the last 5 messages
```bash
tgpublic NovScript -n 5
```

### Get messages and download attachments
```bash
tgpublic NovScript -n 3 --download
```

### Download channel profile picture
```bash
tgpublic NovScript --download-profile
```

### Show member count (along with messages)
```bash
tgpublic NovScript --members
```

### Get only member count (no messages or downloads)
```bash
tgpublic NovScript --only_members
```

### Get JSON output (for script processing)
```bash
tgpublic NovScript -n 10 --json
```

### Combine multiple options
```bash
tgpublic NovScript -n 5 --download --download-profile --members -o my_downloads
```

---

## Detailed Options

| Option | Description |
|--------|-------------|
| `channel` | Telegram channel name (without `@`). If not provided, the program will prompt you. |
| `-n`, `--num-messages` | Number of latest messages to retrieve (default: 2). |
| `-d`, `--download` | Download all message attachments (images, videos, documents). |
| `--download-profile` | Download channel profile picture and save as `{channel}_profile.jpg`. |
| `--members` | Show channel member count (requires a separate request to `t.me/{channel}`). |
| `--only_members` | Retrieve only the member count; do not fetch messages or downloads. |
| `-o`, `--output` | Directory path for saving downloaded files (default: `downloads/`). |
| `--json` | Print output as raw JSON (suitable for automated processing). |
| `-h`, `--help` | Show help. |

---

## Sample Output

### Normal mode (without `--json`)
```
████████╗  ██████╗  ██████╗  ██╗   ██╗ ██████╗  ██╗      ██╗  ██████╗
╚══██╔══╝ ██╔════╝  ██╔══██╗ ██║   ██║ ██╔══██╗ ██║      ██║ ██╔════╝
   ██║    ██║  ███╗ ██████╔╝ ██║   ██║ ██████╔╝ ██║      ██║ ██║
   ██║    ██║   ██║ ██╔═══╝  ██║   ██║ ██╔══██╗ ██║      ██║ ██║
   ██║    ╚██████╔╝ ██║      ╚██████╔╝ ██████╔╝ ███████╗ ██║ ╚██████╗
   ╚═╝     ╚═════╝  ╚═╝       ╚═════╝  ╚═════╝  ╚══════╝ ╚═╝  ╚═════╝

👥 Member count for @NovScript: 32

============================================================
📨 Message 1
ID: 154
Time: 2026-05-27 20:44:02
👁️ Views: 1,234
Text:
Mashallah, the level of our programmers has gone so high that for any project that comes to mind, someone has already published something 10 levels better on GitHub.
Link: https://t.me/NovScript/154
📎 Attachments (1):
   ✅ DZdcjLQDv_guPZzsH_fn1_XJZmB9yUDQuYvCmJg1HOiVuN-yfRtOHjIBkPc3sxCvPYL4gSMI8LydPwCneEi9JgAyA8cuMy4aTdK7SHt91lSwEJD7jTSuxH6JDEcUUfTMG1TGtdejY-F6JIriC3aWOFLYF46T4rhdNmscatoQ0UkzMfvBug5nkx6-wyA2nQzG3CLu36ZZ1RdHhw26haahAil75xAUw9phonnki6Kd6rq8U9ARc5KggDLbR0HKuy4-ZQ7nhveX0gzfJQ5s8wnp3adAQJHdB3nBq8t372CC4kyaI-6bsrs5D3OL9QvC0HOMAR-HG-D3JzgBpB1ZhNcs4Q.jpg (image)
      Path: downloads\DZdcjLQDv_guPZzsH_fn1_XJZmB9yUDQuYvCmJg1HOiVuN-yfRtOHjIBkPc3sxCvPYL4gSMI8LydPwCneEi9JgAyA8cuMy4aTdK7SHt91lSwEJD7jTSuxH6JDEcUUfTMG1TGtdejY-F6JIriC3aWOFLYF46T4rhdNmscatoQ0UkzMfvBug5nkx6-wyA2nQzG3CLu36ZZ1RdHhw26haahAil75xAUw9phonnki6Kd6rq8U9ARc5KggDLbR0HKuy4-ZQ7nhveX0gzfJQ5s8wnp3adAQJHdB3nBq8t372CC4kyaI-6bsrs5D3OL9QvC0HOMAR-HG-D3JzgBpB1ZhNcs4Q.jpg
...
```

### JSON mode
```bash
tgpublic NovScript --only_members --json
```
Output:
```json
{
  "profile": {
    "member_count": 32
  }
}
```

---

## Logging and Errors

- All logs are shown in the console at `INFO` level.
- Serious errors are saved in `tgpublic_errors.log` (max 5 MB, with 3 rotating backups).
- If an unexpected error occurs, a 6-digit code is displayed. You can use this code for troubleshooting by checking the error log.

---

## Development and Contribution

### Running tests
```bash
pytest
```

### Project structure
```
tgpublic/
├── src/tgpublic/
│   ├── cli.py           # Command-line entry point
│   ├── scraper.py       # Main scraper class
│   ├── parsers.py       # HTML parsing with BeautifulSoup
│   ├── downloader.py    # File downloader with resume support (partial)
│   ├── models.py        # Data models (Message, Attachment, ...)
│   ├── config.py        # Constants (URLs, timeout, ...)
│   ├── logging_config.py # Logging configuration
│   └── display.py       # Banner and colored error display
├── py_tests/            # Unit tests (with pytest)
├── tests/               # Manual test scripts (optional)
└── pyproject.toml       # Project settings and dependencies
```

### Adding a new feature
1. Update the model in `models.py` if needed.
2. Write the parsing function in `parsers.py`.
3. Add the corresponding method to `TelegramChannelScraper`.
4. Define the command-line option in `cli.py`.
5. Write unit tests and verify with `pytest`.

---

## License

This project is released under the **MIT** license (see `LICENSE` file).

---

## Contact and Contribution

- Developer: [Dev-vesper](https://github.com/Dev-vesper)
- To report an issue or suggest a feature, open an **Issue** on the GitHub repository.
- Contributions via Pull Request are welcome.

---

**TgPublic** – Simple and fast extraction from public Telegram channels, without needing API or authentication.
