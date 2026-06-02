from pathlib import Path
from unittest.mock import MagicMock, patch

from tgpublic.downloader import FileDownloader


@patch("tgpublic.downloader.requests.get")
def test_download_success(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.headers = {"content-disposition": 'attachment; filename="test.jpg"'}
    mock_response.iter_content.return_value = [b"fake_image_data"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    downloader = FileDownloader()
    result = downloader.download("https://example.com/file", str(tmp_path))

    assert result is not None
    assert result.name == "test.jpg"
    assert result.exists()
    with open(result, "rb") as f:
        assert f.read() == b"fake_image_data"


@patch("tgpublic.downloader.requests.get")
def test_download_uses_fallback_filename(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.headers = {}
    mock_response.url = "https://example.com/abc.unknown"
    mock_response.iter_content.return_value = [b"data"]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    downloader = FileDownloader()
    result = downloader.download("https://example.com/abc", str(tmp_path), filename="fallback.bin")

    assert result.name == "fallback.bin"


@patch("tgpublic.downloader.requests.get")
def test_download_request_error(mock_get, tmp_path):
    import requests as req_lib

    mock_get.side_effect = req_lib.ConnectionError("timeout")

    downloader = FileDownloader()
    result = downloader.download("https://unreachable.com", str(tmp_path))

    assert result is None