import pytest

from app.models import PassportData, VehicleDocumentData
from app.utils.file_utils import get_clean_text, get_summary_text


def test_get_clean_text():
    """Test the get_clean_text function to ensure it correctly removes the confirmation question from the text."""
    # Arrange
    text_with_question = "Some data\n\n🟩 Is this data correct?"
    expected_clean_text = "Some data"
    # Act
    actual_clean_text = get_clean_text(text_with_question)

    # Assert
    assert actual_clean_text == expected_clean_text


@pytest.mark.asyncio
async def test_get_summary_text():
    """Test the get_summary_text function to ensure it generates the correct summary text from passport and vehicle data."""
    # Arrange
    passport_data = PassportData(
        given_names="John",
        surnames="Doe",
        date_of_birth="1990-01-01",
        passport_number="AB123456",
    )
    vehicle_data = VehicleDocumentData(
        vin="123XYZ",
        vehicle_make_and_model="Tesla Model S",
        registration_number="AA0000BB",
    )

    # Act
    summary_text = await get_summary_text(passport_data, vehicle_data)
    assert "John" in summary_text
    assert "Doe" in summary_text
    assert "Tesla Model S" in summary_text
    assert "AB123456" in summary_text
    assert "AA0000BB" in summary_text
    assert "🟩 Is this data correct" in summary_text
