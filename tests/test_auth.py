import pytest
from auth import get_authenticated_service
from unittest.mock import MagicMock, patch
import pickle


@pytest.fixture
def mock_credentials_file(tmp_path):
    """Create a mock credentials file."""
    credentials_file = tmp_path / "client_secrets.json"
    credentials_file.write_text('{"installed": {"client_id": "test_id", "client_secret": "test_secret"}}')
    return str(credentials_file)


def test_valid_credentials(mock_credentials_file, mocker):
    """Test successful authentication with valid credentials."""
    mocker.patch("os.path.exists", return_value=True)

    # Mock a valid serialized credentials object
    mock_serialized_credentials = b'{"valid": true, "token": "mock_access_token"}'
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_serialized_credentials))

    # Mock the deserialization of the credentials
    mock_credentials = MagicMock(valid=True)
    mocker.patch("pickle.load", return_value=mock_credentials)

    # Mock the InstalledAppFlow and YouTube API build
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=MagicMock())
    with patch("googleapiclient.discovery.build", return_value=MagicMock()) as mock_build:
        service = get_authenticated_service()
        assert service is not None
        mock_build.assert_called_once()


def test_missing_credentials_file(mocker):
    """Test behavior when the credentials file is missing."""
    mocker.patch("os.path.exists", return_value=False)

    # Mock the InstalledAppFlow and ensure it is not used
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=MagicMock())

    with pytest.raises(Exception, match="Error during authentication"):
        get_authenticated_service()


def test_expired_token(mocker, mock_credentials_file):
    """Test behavior when the access token is expired."""
    mock_credentials = MagicMock(valid=False, expired=True, refresh_token="mock_refresh_token")
    mocker.patch("os.path.exists", return_value=True)

    # Mock serialized credentials
    mock_serialized_credentials = b'{"expired": true, "refresh_token": "mock_refresh_token"}'
    mocker.patch("builtins.open", mocker.mock_open(read_data=mock_serialized_credentials))

    # Mock deserialization
    mocker.patch("pickle.load", return_value=mock_credentials)

    # Mock token refresh
    mocker.patch("google.auth.transport.requests.Request", return_value=MagicMock())
    mock_credentials.refresh = MagicMock()

    # Mock the YouTube API build
    with patch("googleapiclient.discovery.build", return_value=MagicMock()) as mock_build:
        service = get_authenticated_service()
        assert service is not None
        mock_credentials.refresh.assert_called_once()
        mock_build.assert_called_once()


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
