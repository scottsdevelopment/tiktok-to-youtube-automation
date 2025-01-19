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
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file")

    with patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        service = get_authenticated_service()
        assert service is not None


def test_missing_credentials_file(mocker):
    """Test behavior when the credentials file is missing."""
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.run_console", return_value=MagicMock())

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
    mocker.patch("google.auth.transport.requests.Request")

    with patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        service = get_authenticated_service()

        assert service is not None
        mock_credentials.refresh.assert_called_once()


def test_invalid_credentials_file(mocker, tmp_path):
    """Test behavior when the credentials file is invalid."""
    invalid_credentials_file = tmp_path / "invalid_client_secrets.json"
    invalid_credentials_file.write_text("INVALID_JSON")

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"invalid data"))
    mocker.patch("pickle.load", side_effect=FileNotFoundError("No such file or directory: 'token.pickle'"))

    with pytest.raises(FileNotFoundError, match="No such file or directory: 'token.pickle'"):
        get_authenticated_service()
