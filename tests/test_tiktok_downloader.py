import os
import pytest
from tiktok_downloader import download_tiktok_clips

@pytest.fixture
def mock_download_dir(tmp_path):
    """Create a temporary download directory."""
    return str(tmp_path)

def test_successful_download(mocker, mock_download_dir):
    """Test a successful download scenario."""
    mocker.patch("subprocess.run", return_value=None)
    username = "valid_user"
    
    # Simulate download
    download_tiktok_clips(username, mock_download_dir)
    
    # Check if directory exists
    assert os.path.exists(mock_download_dir)

def test_invalid_username(mocker, mock_download_dir):
    """Test the behavior with an invalid username."""
    mocker.patch("subprocess.run", side_effect=Exception("Invalid username"))
    
    # Expect an exception to be raised
    with pytest.raises(Exception, match="Invalid username"):
        download_tiktok_clips("invalid_user", mock_download_dir)

def test_network_error(mocker, mock_download_dir):
    """Test the behavior during a network error."""
    mocker.patch("subprocess.run", side_effect=Exception("Network error"))
    
    # Expect an exception to be raised
    with pytest.raises(Exception, match="Network error"):
        download_tiktok_clips("valid_user", mock_download_dir)

def test_directory_permission_error(mocker):
    """Test the behavior when directory permissions are restricted."""
    mocker.patch("subprocess.run", return_value=None)
    restricted_dir = "/root/restricted_dir"  # Simulate a directory with no write access
    
    # Expect an exception due to directory permissions
    with pytest.raises(PermissionError):
        download_tiktok_clips("valid_user", restricted_dir)
