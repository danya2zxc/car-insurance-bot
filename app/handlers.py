from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
import app.keyboard as kb
from app.processors import PhotoProcessor
from app.states import Form
from aiogram.types import CallbackQuery
from app.config import s
from app.services.mindee import MindeeService
from app.utils.file_utils import download_user_photo, get_clean_text, get_passport_extracted_text, get_summary_text, get_vehicle_extracted_text
from app.models import PassportData, VehicleDocumentData
# Initialize the router
router = Router()

# --- PRIVATE HELPER FOR THIS MODULE ---
async def _show_summary(message: Message, state: FSMContext):
    """Private helper to show summary and set state. Avoids code duplication."""
    data = await state.get_data()
    passport_data = PassportData.model_validate(data.get("passport_data"))
    vehicle_data = VehicleDocumentData.model_validate(data.get("vehicle_document_data"))
    summary_text = await get_summary_text(passport_data, vehicle_data)
    
    await message.answer(summary_text, reply_markup=kb.document_confirm_kb)
    await state.update_data(summary_text_message=summary_text)
    await state.set_state(Form.waiting_for_summary_confirmation)

# --- Start command handler ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handles the /start command, greets the user, and asks for a passport photo.
    """
    await state.clear()  # Clear any previous state
    await message.answer(f"Hello, {message.from_user.first_name}!👋 Welcome to the insurance bot 🤖\n\n"
                        f"To start, please a send photo of your passport. 🛂")
    await state.set_state(Form.waiting_for_passport)


# --- 1 Passport Photo Handler ---
@router.message(Form.waiting_for_passport, F.photo)
async def handle_passport(message: Message, state: FSMContext, bot: Bot):
    """
    Processes the passport photo using Mindee and asks for confirmation
    """
    text, success, data_obj = await PhotoProcessor.process_photo(message, state, bot, "passport")
    if success and data_obj:
        await state.update_data(passport_data=data_obj.model_dump(),
                                passport_confirm_text=text)
        await message.answer(text, reply_markup=kb.document_confirm_kb)
    elif text:
        await message.answer(text)

# --- 1a. Passport Confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong", "cancel_changing"]), Form.waiting_for_passport)
async def process_passport(callback: CallbackQuery, state: FSMContext):
    """ 
    This function is called when the user confirms or rejects the passport data.
    If the user confirms, it sends a message asking for the vehicle document photo.
    If the user rejects, it asks them to send a new passport photo.
    If the user chooses to cancel changing, it sends a summary of the insurance data and asks
    """


    data = await state.get_data()
    is_changing = data.get("is_changing", False)
    
    if callback.data == "data_ok":
        clean_text = get_clean_text(callback.message.text)
        await callback.message.edit_text(clean_text, reply_markup=None)
        
        if is_changing:
            await state.update_data(is_changing=False)
            await callback.message.answer("✅ Data updated. Let's review the final summary again.")
            await _show_summary(callback.message, state)
        else:
            await callback.message.answer("✅ Passport data confirmed.\n\nNow, please send a photo of your vehicle document 🚗 (registration certificate or insurance policy).")
            await state.set_state(Form.waiting_for_vehicle_document)

    elif callback.data == "data_wrong":    
        
        msg_with_cancel_button = await callback.message.edit_text(
            "❌ Passport data is incorrect. Please send a new photo of your passport.",
            reply_markup=kb.cancel_only_kb,
        )
        await state.update_data(msg_to_edit_id=msg_with_cancel_button.message_id)
        await state.set_state(Form.waiting_for_passport)

    elif callback.data == "cancel_changing":
        data = await state.get_data()
        passport_confirm_text = data.get('passport_confirm_text', 'No data available.')
        await callback.message.edit_text(passport_confirm_text, reply_markup=kb.document_confirm_kb)
        await state.set_state(Form.waiting_for_passport)
        
    await callback.answer()

# --- 2. Vehicle Document Photo Handler ---
@router.message(Form.waiting_for_vehicle_document, F.photo)
async def handle_vehicle_document(message: Message, state: FSMContext, bot: Bot):
    """
    Processes the vehicle document photo using Mindee and asks for confirmation.
    """
    text, success, data_obj = await PhotoProcessor.process_photo(message, state, bot, "vehicle")
    if success and data_obj:

        await state.update_data(
            vehicle_document_data=data_obj.model_dump(),
            vehicle_confirm_text=text
        )
        await message.answer(text, reply_markup=kb.document_confirm_kb)
    elif text:
        await message.answer(text)

# --- 2a. Vehicle Document Confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong", "cancel_changing"]), Form.waiting_for_vehicle_document)
async def process_vehicle_document(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user confirms or rejects the vehicle document data.
    If the user confirms, it sends a message asking for the summary confirmation.
    If the user rejects, it asks them to send a new vehicle document photo.
    If the user chooses to cancel changing, it sends a summary of the insurance data and asks
    for confirmation.
    '''

    data = await state.get_data()
    is_changing = data.get("is_changing", False)
    
    if callback.data == "data_ok":
        clean_text = get_clean_text(callback.message.text)
        await callback.message.edit_text(clean_text, reply_markup=None)
        

        if is_changing:
            await state.update_data(is_changing=False)
            await callback.message.answer("✅ Data updated. Let's review the final summary again.")
            
        
        else:
            await callback.message.answer(
                "✅ Vehicle document data confirmed.\n\n"
                "Now, let's summarize the data you provided. Please, check the final data below and confirm if it is correct."
            )
        await _show_summary(callback.message, state)
       

    elif callback.data == "data_wrong":
    
        msg_with_cancel_button = await callback.message.edit_text(
            "❌ OK. Please send a new photo of your vehicle document.",
            reply_markup=kb.cancel_only_kb,
        )
        await state.update_data(msg_to_edit_id=msg_with_cancel_button.message_id)
        await state.set_state(Form.waiting_for_vehicle_document)
    
    elif callback.data == "cancel_changing":
        vehicle_confirm_text = data.get("vehicle_confirm_text", "No data available.")
        await callback.message.edit_text(
            vehicle_confirm_text, reply_markup=kb.document_confirm_kb
        )
        await state.set_state(Form.waiting_for_vehicle_document)
    
    
    await callback.answer()


# --- 3. Summary Confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong"]), Form.waiting_for_summary_confirmation)
async def process_summary(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user confirms or rejects the summary data.
    If the user confirms, it sends a message asking for the insurance price confirmation.
    If the user rejects, it asks them to change the photo.
    '''
    data = await state.get_data()
    summary_text_message = data.get('summary_text_message', 'No data available.')
    clean_text = get_clean_text(summary_text_message)

    if callback.data == "data_ok":
        await callback.message.edit_text(
        clean_text,
        reply_markup=None
    )
        await callback.message.answer(f"✅ Summary data confirmed.\n\n"
            f"The insurance price is: {s.insurance_price} USD. Do you agree?.\n\n"
            f"Please choice if you want to proceed with the insurance purchase.",
            reply_markup=kb.confirm_kb)

        await state.set_state(Form.waiting_for_price_confirmation)

    elif callback.data == "data_wrong":
        await callback.message.edit_text(f"{clean_text}\n\n❌ Summary data is incorrect. Choice which photo you want to change.", reply_markup=kb.change_photo_kb)
        await state.set_state(Form.waiting_for_change_choice)
    await callback.answer()    


# --- 4. Price Confirmation ---
@router.callback_query(F.data.in_(["confirm_yes","confirm_no"]), Form.waiting_for_price_confirmation)
async def handle_price_confirmation(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user confirms or rejects the insurance price.
    If the user confirms, it sends a message thanking them for using the service.
    If the user rejects, it sends a message saying that the price is the only available price
    and asks them to start over with /start.
    '''
    if callback.data == "confirm_yes":

        # TODO implement logic for processing Generate a dummy insurance policy document using OpenAI (assuming use of a template or a
        # TODO pre -formatted text).

        await callback.message.edit_text("✅ Insurance purchase confirmed. Thank you for using our service! 🎉", reply_markup=None)
        await state.clear()
    elif callback.data == "confirm_no":
        await callback.message.edit_text("❌ We are sorry that the price did not suit you. This is the only available price. If you change your mind, please start over with /start.", reply_markup=None)
        await state.clear()

    await callback.answer()


# --- Callback query handler for changing photos ---
@router.callback_query(
    F.data.in_(
        ["change_passport", "change_vehicle_document", "cancel_changing"]
    ),
    Form.waiting_for_change_choice,
)
async def process_change_choice(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user chooses to change a photo or cancel the changing.
    It handles the following cases:
    1. If the user chooses to change the passport photo, it prompts them to send a new passport photo.
    2. If the user chooses to change the vehicle document photo, it prompts them to send a new vehicle document photo.
    3. If the user chooses to cancel the changing, it sends a summary of the insurance data and asks for confirmation.
    '''
    if callback.data == "change_passport":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("🛂 Please send a new photo of your passport.")
        await state.update_data(is_changing=True)
        await state.set_state(Form.waiting_for_passport)

    elif callback.data == "change_vehicle_document":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("🚗 Please send a new photo of your vehicle.")
        await state.update_data(is_changing=True)
        await state.set_state(Form.waiting_for_vehicle_document)

    elif callback.data == "cancel_changing":
        await callback.message.delete()
        await _show_summary(callback.message, state)
        
    await callback.answer()
