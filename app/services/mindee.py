from app.config import s
from mindee import ClientV2, InferenceParameters

from app.models import PassportData, VehicleDocumentData

# Initialize Mindee client with API key
mindee_client = ClientV2(api_key=s.mindee_passport_api_key)


# --- MindeeService Class ---
class MindeeService:
    def __init__(self, api_key: str, model_id: str):
        '''
        Initialize the MindeeService with API key and model ID.
        '''
        self.client = ClientV2(api_key=api_key)
        self.params = InferenceParameters(model_id=model_id, rag=False)


    async def process_passport_photo(self, file):
        '''
        Process the passport photo and extract data using Mindee API.
        :param file: The file object containing the passport photo.
        :return: Extracted text or None if the photo is not valid.
        '''
        input_doc = self.client.source_from_file(file)
        result = self.client.enqueue_and_get_inference(input_doc, params=self.params)
        
        passport_fields = result.inference.result.fields
        
        if None in [passport_fields.get("given_names").value,passport_fields.get("surnames").value, passport_fields.get("passport_number").value]:
            return None
        
        
        
        
        return PassportData.model_validate(passport_fields)

    async def process_vehicle_document_photo(self, file):
        '''
        Process the vehicle document photo and extract data using Mindee API.
        :param file: The file object containing the vehicle document photo.
        :return: Extracted text or None if the photo is not valid.
        '''
        input_doc = self.client.source_from_file(file)
        result = self.client.enqueue_and_get_inference(input_doc, params=self.params)
        
        vehicle_fields = result.inference.result.fields

        if vehicle_fields.get("vin").value == "null":
            return None
        
        return VehicleDocumentData.model_validate(vehicle_fields)
