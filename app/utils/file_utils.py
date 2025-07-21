import io
from app.models import PassportData, VehicleDocumentData


async def download_user_photo(photo, bot, name: str):
    '''
    Download the user's photo from the message and return it as a file-like object.
    The file will be saved with the provided name.
    '''
    file_info = await bot.get_file(photo.file_id)
    downloaded = await bot.download_file(file_info.file_path)
    
    if not hasattr(downloaded, 'name'):
        downloaded.name = name
        
    return downloaded

# --- Function to clean text by removing the confirmation question ---
def get_clean_text(original_text: str) -> str:
    return original_text.rsplit("\n\n🟩 Is this data correct?", 1)[0]

# --- Function to get passport extracted text ---
async def get_passport_extracted_text(mindee_data: PassportData | None) -> str:
    
    
    
    extracted_text = (
        f"🌐 Check the recognized passport data:\n"
        f"Name: {mindee_data.given_names}\n"
        f"Surname: {mindee_data.surnames}\n"
        f"Date of birth: {mindee_data.date_of_birth}\n"
        f"Passport series/number: {mindee_data.passport_number}\n"
        f"Date of issue: {mindee_data.date_of_issue}\n"
        f"Date of expiry: {mindee_data.date_of_expiry}\n\n"
        f"🟩 Is this data correct?"
    )
    
    
    

    
    return extracted_text


async def get_vehicle_extracted_text(mindee_data: VehicleDocumentData | None) -> str:
    
    extracted_text = (
        f"🚗 Check the recognized vehicle document data:\n"
        f"VIN: {mindee_data.vin}\n"
        f"Model: {mindee_data.model}\n"
        f"Registration Number: {mindee_data.reg_number}\n"
        f"Document Number: {mindee_data.doc_number}\n"
        
        f"\n🟩 Is this data correct?"
    )
    return extracted_text


# --- Utility function to get summary ---
async def get_summary_text(passport_data, vehicle_data):
    """A helper function to generate and send the final summary message."""
    summary_text = (
        f"📝 Please, check the final data:\n\n"
        f"👤 Owner data:\n"
        f"  - Name: {passport_data.given_names}\n"
        f"  - Surname: {passport_data.surnames}\n"
        f"  - Date of birth: {passport_data.date_of_birth}\n"
        f"  - Passport series/number: {passport_data.passport_number}\n\n"
        f"🚗 Vehicle data:\n"
        f"  - VIN: {vehicle_data.vin}\n"
        f"  - Model: {vehicle_data.model}\n"
        f"  - Registration Number: {vehicle_data.reg_number}\n\n"
        f"🟩 Is this data correct?"
    )
    return summary_text



