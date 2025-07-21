from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional


# --- Data models for Mindee API responses ---
class PassportData(BaseModel):
    '''
    Data model for passports extracted from photos.
    This model includes fields for given names, surnames, date of birth, passport number,
    date of issue, and date of expiry.
    '''
    given_names: Optional[str] = Field(default="N/A", description="Given names from the passport")
    surnames: Optional[str] = Field(default="N/A", description="Surnames from the passport" )
    date_of_birth: Optional[str] = Field(default="N/A", description="Date of birth from the passport")
    passport_number: Optional[str] = Field(default="N/A", description="Passport series and number")
    date_of_issue: Optional[str] = Field(default="N/A", description="Date of issue of the passport")
    date_of_expiry: Optional[str] = Field(default="N/A", description="Date of expiry of the passport")

    @field_validator('*', mode='before')
    @classmethod
    def convert_to_string(cls, v: Any) -> str:
        '''
        Convert all fields to string, returning "N/A" if the value is None.
        '''
        if v is None or str(v) == "None":
            return "N/A"
        return str(v)


# --- Data model for vehicle documents extracted from photos ---
class VehicleDocumentData(BaseModel):
    '''
    Data model for vehicle documents extracted from photos.
    This model includes fields for vehicle make and model, registration number, VIN, and document number
    '''
    vin: Optional[str] = Field(default="N/A", description="VIN of the vehicle")
    model: Optional[str] = Field(alias="vehicle_make_and_model", default="N/A", description="Make and model of the vehicle")
    reg_number: Optional[str] = Field(alias="registration_number",default="N/A", description="Registration number of the vehicle")
    doc_number: Optional[str] = Field(alias="document_series_and_number", default="N/A", description="Document series and number")

    @field_validator('*', mode='before')
    @classmethod
    def convert_to_string(cls, v: Any) -> str:
        '''
        Convert all fields to string, returning "N/A" if the value is None.
        '''
        if v is None or str(v) == "None":
            return "N/A"
        return str(v)

