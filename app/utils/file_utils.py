


async def download_user_photo(photo, bot, name: str):
    '''
    Download the user's photo from the message and return it as a file-like object.
    The file will be saved with the provided name.
    '''
    file_info = await bot.get_file(photo.file_id)
    downloaded = await bot.download_file(file_info.file_path)
    
    if not hasattr(downloaded, 'name'):
        downloaded.name = name
        
    return downloaded,photo.file_id

# --- Function to clean text by removing the confirmation question ---
def get_clean_text(original_text: str) -> str:
    return original_text.rsplit("\n\n🟩 Is this data correct?", 1)[0]


