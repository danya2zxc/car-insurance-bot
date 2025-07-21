
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from app.utils import file_utils
import app.keyboard as kb
from app.states import Form
from aiogram.types import InputMediaPhoto, CallbackQuery
from app.config import s
from app.services.mindee import MindeeService
from app.utils.file_utils import download_user_photo, get_clean_text
from app.models import PassportData, VehicleDocumentData
# Initialize the router
router = Router()



# --- Start command handler ---
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handles the /start command, greets the user, and asks for a passport photo.
    """
    await state.clear()  # Clear any previous state
    await message.answer(f"Hello, {message.from_user.first_name}!👋 Welcome to the insurance bot 🤖\n\n"
                        f"For start assistance with insurance, please, send photo of you passport. 🛂")
    await state.set_state(Form.waiting_for_passport)


# --- Passport Photo Handler ---
@router.message(Form.waiting_for_passport, F.photo)
async def handle_passport(message: Message, state: FSMContext, bot: Bot):
    """
    Processes the passport photo using Mindee and asks for confirmation.
    """
    
    
    processing_msg = await message.answer("✨ Photo received, processing...")
    file, file_id = await download_user_photo(message.photo[-1], bot, name="passport_photo.jpg")
    
    try:
        mindee = MindeeService(api_key=s.mindee_passport_api_key, model_id=s.model_passport_id)
        mindee_data: PassportData | None = await mindee.process_passport_photo(file)

        
        if not mindee_data:
            await processing_msg.delete()
            await message.answer("🛑 Passport photo is not valid. Please send a clear photo of your passport.")
            return
        
        
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
        

        await state.update_data(
            passport_photo_id=file_id,
            passport_data=mindee_data.model_dump(),
            passport_confirm_text=extracted_text
        )
        
        await processing_msg.delete()  # delete the processing message
        await message.answer(extracted_text, reply_markup=kb.document_confirm_kb)
        
    except Exception as e:
        print(f"Error processing passport photo: {e}")
        await processing_msg.edit_text("🛑 There was an error processing your passport photo. Please try again with a clearer photo.")
        return
    
    
# --- Callback query handler for passport confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong"]), Form.waiting_for_passport)
async def process_passport(callback: CallbackQuery, state: FSMContext):
    """ 
    This function is called when the user confirms or rejects the passport data.
    If the user confirms, it sends a message asking for the vehicle document.
    If the user rejects, it asks them to send a new passport photo.
    """
    clean_text = get_clean_text(callback.message.text)
    if callback.data == "data_ok":
        await callback.message.edit_text(clean_text, reply_markup=None)
        await callback.message.answer("✅ Passport data confirmed.\n\nNow, please send a photo of your vehicle document 🚗 (registration certificate or insurance policy).")
        await state.set_state(Form.waiting_for_vehicle_document)
    
    elif callback.data == "data_wrong":    
        # await callback.message.edit_text(clean_text, reply_markup=None)
        await callback.message.edit_text(f"{clean_text}\n\n❌ Passport data is incorrect. Please send a new photo of your passport.",reply_markup=kb.cancel_only_kb)
        await state.set_state(Form.waiting_for_passport)
    
    await callback.answer()

# --- Callback query handler for canceling passport change ---
@router.callback_query(F.data == "cancel_changing_passport", Form.waiting_for_passport)
async def cancel_passport_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    passport_confirm_text = data.get('passport_confirm_text', 'No data available.')
    await callback.message.edit_text(passport_confirm_text, reply_markup=kb.document_confirm_kb)
    await state.set_state(Form.waiting_for_passport)
    await callback.answer()


# --- Vehicle Document Photo Handler ---
@router.message(Form.waiting_for_vehicle_document, F.photo)
async def handle_vehicle_document(message: Message, state: FSMContext, bot: Bot):
    """
    Processes the vehicle document photo using Mindee and asks for confirmation.
    """
    processing_msg = await message.answer("✨ Photo received, processing...")
    file, file_id = await download_user_photo(message.photo[-1], bot, name="vehicle_document.jpg")
    
    try:
        mindee  = MindeeService(api_key=s.mindee_vehicle_document_api_key, model_id=s.model_vehicle_document_id)
        mindee_data: VehicleDocumentData | None = await mindee.process_vehicle_document_photo(file)
        
        if not mindee_data:
            await processing_msg.edit_text("🛑 Vehicle document photo is not valid. Please send a clear photo of your vehicle document.")
            return
        
        
        extracted_text = (
            f"🚗 Check the recognized vehicle document data:\n"
            f"VIN: {mindee_data.vin}\n"
            f"Model: {mindee_data.model}\n"
            f"Registration Number: {mindee_data.reg_number}\n"
            f"Document Number: {mindee_data.doc_number}\n"
            
            f"\n🟩 Is this data correct?"
        )
        await state.update_data(
            vehicle_document_photo_id=file_id,
            vehicle_document_data=mindee_data.model_dump(),
            vehicle_confirm_text=extracted_text
        )
        await processing_msg.delete()  # delete the processing message
        await message.answer(extracted_text, reply_markup=kb.document_confirm_kb)
    except Exception as e:
        print(f"Error processing vehicle document photo: {e}")
        await message.answer("🛑 There was an error processing your vehicle document photo. Please try again with a clearer photo.")
        return

# --- Callback query handler for vehicle document confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong"]), Form.waiting_for_vehicle_document)
async def process_vehicle_document(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user confirms or rejects the vehicle document data.
    If the user confirms, it sends a message asking for the summary confirmation.
    If the user rejects, it asks them to send a new vehicle document photo.'''
    
    clean_text = get_clean_text(callback.message.text)
    
    if callback.data == "data_ok":
        
        # first, we need to get the user data from the FSM context
        user_data = await state.get_data()
        
        
        passport_data = PassportData.model_validate(user_data.get('passport_data', {}))
        vehicle_data = VehicleDocumentData.model_validate(user_data.get('vehicle_document_data', {}))
        
        await callback.message.edit_text(clean_text, reply_markup=None)
        await callback.message.answer("✅ Vehicle document data confirmed.\n\nNow, let's summarize the data you provided. Please, check the final data below and confirm if it is correct.")
        
        
        if not passport_data or not vehicle_data:
            await callback.message.answer("❗️ Missing data. Please ensure both passport and vehicle document photos are processed correctly.")
            await state.clear()
            return
        
        
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
        
        await callback.message.answer(summary_text, reply_markup=kb.document_confirm_kb)
        await state.update_state(summary_confirm_text=summary_text)
        await state.set_state(Form.waiting_for_summary_confirmation)
    
    elif callback.data == "data_wrong":
        
        await callback.message.edit_text(f"{clean_text}\n\n❌ Vehicle document data is incorrect. Please send a new photo of your vehicle document.",  reply_markup=kb.cancel_only_kb)
        await state.set_state(Form.waiting_for_vehicle_document)
    
    await callback.answer()


@router.callback_query(F.data == "cancel_changing_passport", Form.waiting_for_vehicle_document)
async def cancel_vehicle_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vehicle_confirm_text = data.get('vehicle_confirm_text', 'No data available.')
    await callback.message.edit_text(vehicle_confirm_text, reply_markup=kb.document_confirm_kb)
    await state.set_state(Form.waiting_for_vehicle_document)
    await callback.answer()


# --- Summary Confirmation Handlers ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong"]), Form.waiting_for_summary_confirmation)
async def process_summary(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user confirms or rejects the summary data.
    If the user confirms, it sends a message with the insurance price and asks for confirmation.
    If the user rejects, it asks which photo they want to change.
    '''
    data = await state.get_data()
    summary_text = data.get('summary_text', 'No data available.')
    clean_text = get_clean_text(summary_text)
    
    
    
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
        await callback.message.edit_text(f"{clean_text}\n\n❌ Summary data is incorrect. Please choice which photo you want to change.", reply_markup=kb.change_photo_kb)
        await state.set_state(Form.waiting_for_change_choice)
    await callback.answer()    
    
    
    
# --- Callback query handler for price confirmation ---
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
@router.callback_query(F.data.in_(["change_passport", "change_vehicle_document", "cancel_changing_passports"]), Form.waiting_for_change_choice)
async def process_change_choice(callback: CallbackQuery, state: FSMContext):
    '''
    This function is called when the user chooses to change a photo or cancel the changing.
    It handles the following cases:
    1. If the user chooses to change the passport photo, it prompts them to send a new passport photo.
    2. If the user chooses to change the vehicle document photo, it prompts them to send a new vehicle document photo.
    3. If the user chooses to cancel the changing, it sends a summary of the insurance data and asks for confirmation.
    '''
    if callback.data == "change_passport":
        await callback.message.answer("Please send a new photo of your passport.")
        await state.set_state(Form.waiting_for_passport)

    elif callback.data == "change_vehicle":
        await callback.message.answer("Please send a new photo of your vehicle.")
        await state.set_state(Form.waiting_for_vehicle_document)

    elif callback.data == "cancel_changing_passports":
        data = await state.get_data()
        summary_text = data.get('summary_text', 'No data available.')
        await callback.message.edit_text(summary_text, reply_markup=kb.document_confirm_kb)

        await state.set_state(Form.waiting_for_change_choice)

    await callback.answer()

