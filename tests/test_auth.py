import pytest
from auth import get_authenticated_service
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_credentials_file(tmp_path):
    """Create a mock credentials file."""
    credentials_file = tmp_path / "client_secrets.json"
    credentials_file.write_text('{"installed": {"client_id": "test_id"}}')
    return str(credentials_file)


def test_valid_credentials(mock_credentials_file, mocker):
    """Test successful authentication with valid credentials."""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"mocked_token"))
    mocker.patch("pickle.load", return_value=MagicMock(valid=True))
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=MagicMock())

    with patch("googleapiclient.discovery.build", return_value=MagicMock()) as mock_build:
        service = get_authenticated_service()
        assert service is not None
        mock_build.assert_called_once()


def test_missing_credentials_file(mocker):
    """Test behavior when the credentials file is missing."""
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file", return_value=MagicMock())

    with pytest.raises(Exception, match="Error during authentication"):
        get_authenticated_service()


def test_expired_token(mocker, mock_credentials_file):
    """Test behavior when the access token is expired."""
    mock_credentials = MagicMock()
    mock_credentials.valid = False
    mock_credentials.expired = True
    mock_credentials.refresh_token = "test_refresh_token"

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"mocked_token"))
    mocker.patch("pickle.load", return_value=mock_credentials)
    mocker.patch("google.auth.transport.requests.Request", return_value=MagicMock())

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
    mocker.patch("builtins.open", mocker.mock_open(read_data="INVALID_JSON"))
    mocker.patch("pickle.load", side_effect=Exception("Invalid credentials file"))

    with pytest.raises(Exception, match="Invalid credentials file"):
        get_authenticated_service()
