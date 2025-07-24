from unittest.mock import AsyncMock, patch

import pytest

from app.models import PassportData, VehicleDocumentData
from app.services.openai import OpenAIService


@pytest.mark.asyncio
async def test_generate_policy_text_mocks_api_call():
    """
    Tests that OpenAIService.generate_policy_text correctly calls the API
    and returns a formatted result, using a mock for the API client.
    """
    # Arrange: Mock the entire OpenAI client
    with patch("app.services.openai.AsyncOpenAI") as mock_openai_constructor:
        # 1. Create a mock for the client instance
        mock_client = AsyncMock()

        # 2. Configure the mock's method to return a predictable structure
        mock_client.chat.completions.create.return_value.choices = [
            type("obj", (), {"message": type("obj", (), {"content": "<b>Mocked Policy HTML</b>"})})
        ]
        mock_openai_constructor.return_value = mock_client

        # 3. Instantiate our service (it will now use the mocked client)
        service = OpenAIService(api_key="fake-key", model="gpt-4o-mini")

        # 4. Prepare test data
        passport_data = PassportData(given_names="John", surnames="Doe")
        vehicle_data = VehicleDocumentData(model="Tesla", reg_number="A123")

        # Act: Call the method we want to test
        result = await service.generate_policy_text(passport_data, vehicle_data)

        # Assert: Verify the outcome
        mock_client.chat.completions.create.assert_called_once()
        assert "<b>Mocked Policy HTML</b>" in result
