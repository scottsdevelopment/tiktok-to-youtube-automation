import os
import pytest
from youtube_uploader import upload_to_youtube, process_and_upload_clips
from unittest.mock import MagicMock

@pytest.fixture
def mock_youtube_service():
    """Create a mock YouTube API service."""
    return MagicMock()

@pytest.fixture
def mock_download_dir(tmp_path):
    """Create a temporary directory for testing video uploads."""
    test_video = tmp_path / "test_video.mp4"
    test_metadata = tmp_path / "test_video.json"
    
    # Create a dummy video file
    test_video.write_text("dummy video content")
    
    # Create a dummy metadata file
    test_metadata.write_text('{"text": "Test Title", "webVideoUrl": "http://example.com"}')
    
    return tmp_path

def test_successful_upload(mock_youtube_service):
    """Test a successful video upload."""
    video_path = "test_video.mp4"
    title = "Test Video Title"
    description = "Test Video Description"
    
    # Mock YouTube API response
    mock_youtube_service.videos().insert().execute.return_value = {"id": "12345"}
    
    # Call the upload function
    upload_to_youtube(mock_youtube_service, video_path, title, description)
    
    # Assert that the API was called with the correct parameters
    mock_youtube_service.videos().insert.assert_called_once()
    mock_youtube_service.videos().insert().execute.assert_called_once()

def test_invalid_video_file(mock_youtube_service):
    """Test behavior when the video file does not exist."""
    video_path = "non_existent_video.mp4"
    title = "Invalid Video"
    description = "Invalid video file test."
    
    # Expect an exception due to the missing file
    with pytest.raises(FileNotFoundError):
        upload_to_youtube(mock_youtube_service, video_path, title, description)

def test_process_and_upload_clips(mock_youtube_service, mock_download_dir):
    """Test the end-to-end process of uploading videos."""
    # Mock the YouTube service
    mock_youtube_service.videos().insert().execute.return_value = {"id": "12345"}
    
    # Call the function to process and upload clips
    process_and_upload_clips(mock_download_dir)
    
    # Assert that videos are uploaded
    mock_youtube_service.videos().insert.assert_called()

def test_quota_exceeded_error(mock_youtube_service):
    """Test handling when YouTube API quota is exceeded."""
    video_path = "test_video.mp4"
    title = "Test Video"
    description = "Quota exceeded test"
    
    # Mock YouTube API quota error
    mock_youtube_service.videos().insert().execute.side_effect = Exception("Quota Exceeded")
    
    # Expect an exception and ensure error is logged
    with pytest.raises(Exception, match="Quota Exceeded"):
        upload_to_youtube(mock_youtube_service, video_path, title, description)
