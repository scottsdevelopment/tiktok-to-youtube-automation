import logging
import pytest
from logger import setup_logger


def test_logger_configuration(tmp_path, mocker):
    """Test that the logger is configured correctly."""
    mock_file_handler = mocker.patch("logging.FileHandler", autospec=True)
    mock_stream_handler = mocker.patch("logging.StreamHandler", autospec=True)

    setup_logger()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_logger_output(capsys):
    """Test logger outputs messages to the console."""
    setup_logger()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("Test log message")

    captured = capsys.readouterr()
    assert "Test log message" in captured.out


def test_log_file_creation(tmp_path, mocker):
    """Test that a log file is created and written to."""
    log_file = tmp_path / "test_log_file.log"

    # Patch the FileHandler to use a temporary file
    mocker.patch("logging.FileHandler", return_value=logging.FileHandler(log_file))
    setup_logger()

    # Log a test message
    logger = logging.getLogger()
    logger.info("Logging to file test")

    # Verify the log file was created and contains the message
    assert log_file.exists()
    with open(log_file, "r") as file:
        log_contents = file.read()
    assert "Logging to file test" in log_contents
