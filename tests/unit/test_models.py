from app.models import PassportData


def test_passport_data_validator():
    """Test the PassportData model to ensure it correctly handles missing fields and defaults."""
    # Arrange
    raw_data = {
        "given_names": "John",
        "surnames": None,  # This should default to "N/A"
        "date_of_birth": None,  # This should default to "N/A"
        "passport_number": "AB123456",
    }

    # Act
    passport = PassportData.model_validate(raw_data)

    # Assert
    assert passport.given_names == "John"
    assert passport.surnames == "N/A"
    assert passport.passport_number == "AB123456"
    assert passport.date_of_birth == "N/A"  # check default value
