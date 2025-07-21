from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    telegram_bot_token: str   
    mindee_passport_api_key: str
    model_passport_id: str = "6923c5e9-1db5-44c5-bc33-9c67939a565d"
    mindee_vehicle_document_api_key: str
    model_vehicle_document_id: str = "ca32abe5-2f40-46fa-b119-76b687842c9d"
    
    
    insurance_price: int = 100  # Default insurance price
    
    
    class Config:
        env_file = ".env"
s = Settings()

