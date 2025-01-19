import pytest
from auth import get_authenticated_service
from unittest.mock import MagicMock, patch
import pickle


@pytest.fixture
def mock_credentials_file(tmp_path):
    """Create a mock credentials file."""
    credentials_file = tmp_path / "client_secrets.json"
    credentials_file.write_text('{"installed": {"client_id": "test_id"}}')
    return str(credentials_file)


def test_valid_credentials(mock_credentials_file, mocker):
    """Test successful authentication with valid credentials."""
    mocker.patch("os.path.exists", return_value=True)

    # Mock serialized credentials
    mock_serialized_credentials = {"valid": True, "token": "mock_token"}
    mocker.patch("pickle.load", return_value=mock_serialized_credentials)

    # Mock the discovery build
    mock_discovery_doc = {
        "rootUrl": "https://www.googleapis.com/",
        "servicePath": "youtube/v3/"
    }
    mocker.patch("googleapiclient.discovery.build", return_value=mock_discovery_doc)

    service = get_authenticated_service()
    assert service is not None


def test_missing_credentials_file(mocker):
    """Test behavior when the credentials file is missing."""
    mocker.patch("os.path.exists", return_value=False)

    with pytest.raises(Exception, match="Error during authentication"):
        get_authenticated_service()


def test_expired_token(mocker, mock_credentials_file):
    """Test behavior when the access token is expired."""
    mock_credentials = {"valid": False, "expired": True, "refresh_token": "mock_refresh"}
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("pickle.load", return_value=mock_credentials)

    service = get_authenticated_service()
    assert service is not None


def test_invalid_credentials_file(mocker, tmp_path):
    """Test behavior when the credentials file is invalid."""
    invalid_credentials_file = tmp_path / "invalid_client_secrets.json"
    invalid_credentials_file.write_text("INVALID_JSON")

    mocker.patch("os.path.exists", return_value=True)

    # Mock invalid JSON in the credentials file
    mocker.patch("builtins.open", mocker.mock_open(read_data="INVALID_JSON"))

    # Ensure an error is raised during deserialization
    mocker.patch("pickle.load", side_effect=Exception("Invalid credentials file"))

    with pytest.raises(Exception, match="Invalid credentials file"):
        get_authenticated_service()
