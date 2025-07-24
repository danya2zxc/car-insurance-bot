from unittest.mock import AsyncMock, patch

import pytest

from app.models import PassportData
from app.processors import PhotoProcessor


@pytest.mark.asyncio
async def test_process_photo_success():
    """Test the process_photo method of PhotoProcessor to ensure it processes a passport photo correctly."""
    # Arrange: Mock the bot, message, and state
    mock_bot = AsyncMock()
    mock_message = AsyncMock()
    mock_state = AsyncMock()

    # Setup mock for state.get_data to return an empty dict
    mock_state.get_data.return_value = {}

    # Create a mock for the Mindee data
    mock_mindee_data = PassportData(given_names="John", surnames="Doe")

    # Patch the download_user_photo function to return a mock file-like object
    with (
        patch("app.processors.download_user_photo", new_callable=AsyncMock),
        patch("app.processors.MindeeService") as mock_mindee_service,
    ):
        mock_mindee_instance = mock_mindee_service.return_value

        async def mock_async_process(*args, **kwargs):
            return mock_mindee_data

        mock_mindee_instance.process_passport_photo = mock_async_process
        # Act: Call the process_photo method
        text, success, data_obj = await PhotoProcessor.process_photo(mock_message, mock_state, mock_bot, "passport")

        # Assert: Check that the method returns the expected text and success status
        assert success is True
        assert data_obj == mock_mindee_data
        assert "John" in text
        assert "Doe" in text
        # Check that bot delete message
        mock_message.answer.assert_called_with("✨ Photo received, processing...")
        mock_message.answer.return_value.delete.assert_called_once()
