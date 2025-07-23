from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import s
from app.services.mindee import MindeeService
from app.utils.file_utils import (
    download_user_photo,
    get_passport_extracted_text,
    get_vehicle_extracted_text,
)


class PhotoProcessor:
    """
    Unique method for Processing photo
    Return (text_for_user, flag_of_success, data_obj)"""

    @staticmethod
    async def process_photo(message: Message, state: FSMContext, bot: Bot, doc_type: str):
        data = await state.get_data()
        msg_to_edit_id = data.get("msg_to_edit_id")
        if msg_to_edit_id:
            try:
                await bot.edit_message_reply_markup(
                    chat_id=message.chat.id, message_id=msg_to_edit_id, reply_markup=None
                )
                await state.update_data(msg_to_edit_id=None)
            except Exception as e:
                print(f"Error editing message: {e}")

        processing_msg = await message.answer("✨ Photo received, processing...")
        file = await download_user_photo(message.photo[-1], bot, name=f"{doc_type}.jpg")
        mindee = None
        extracted_text = ""
        try:
            if doc_type == "passport":
                mindee = MindeeService(api_key=s.mindee_passport_api_key, model_id=s.model_passport_id)
                mindee_data = await mindee.process_passport_photo(file)

                if not mindee_data:
                    await processing_msg.edit_text(
                        "🛑 Passport photo is not valid. Please send a clear photo of your passport."
                    )
                    return None, False, None

                extracted_text = await get_passport_extracted_text(mindee_data)

            elif doc_type == "vehicle":
                mindee = MindeeService(api_key=s.mindee_vehicle_document_api_key, model_id=s.model_vehicle_document_id)
                mindee_data = await mindee.process_vehicle_document_photo(file)

                if not mindee_data:
                    await processing_msg.edit_text(
                        "🛑 Vehicle document photo is not valid. Please send a clear photo of your vehicle document."
                    )
                    return None, False, None
                extracted_text = await get_vehicle_extracted_text(mindee_data)

            await processing_msg.delete()
            return extracted_text, True, mindee_data

        except Exception as e:
            print(f"🛑 Error processing photo: {e}")
            await processing_msg.edit_text("🛑 An unexpected error occurred. Please try again.")
            return None, False, None
