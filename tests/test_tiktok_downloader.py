import os
import pytest
from tiktok_downloader import download_tiktok_clips

def test_successful_download(mocker):
    mocker.patch("subprocess.run", return_value=None)
    username = "valid_user"
    download_dir = "./test_download"
    os.makedirs(download_dir, exist_ok=True)
    download_tiktok_clips(username, download_dir)
    assert os.path.exists(download_dir)

def test_invalid_username(mocker):
    mocker.patch("subprocess.run", side_effect=Exception("Invalid username"))
    with pytest.raises(Exception):
        download_tiktok_clips("invalid_user", "./test_download")
