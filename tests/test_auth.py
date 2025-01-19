import pytest
from auth import get_authenticated_service

def test_valid_credentials(mocker):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("pickle.load", return_value=None)
    service = get_authenticated_service()
    assert service is not None

def test_missing_credentials(mocker):
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(Exception):
        get_authenticated_service()
