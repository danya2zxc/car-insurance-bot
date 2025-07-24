from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

import app.keyboard as kb
from app.config import s
from app.models import PassportData, VehicleDocumentData
from app.processors import PhotoProcessor
from app.services.openai import openai_service
from app.states import Form
from app.utils.file_utils import get_clean_text, get_summary_text

# Initialize the router
router = Router()

HELP_TEXT = (
    "Hello! I'm your car insurance assistant. 🤖\n\n"
    "To start the process of getting your insurance policy, please use the /start command.\n\n"
    "If you get stuck at any point, you can always use the /cancel command to restart the process from the beginning."
)


# --- Command Handlers ---
@router.message(Command("help"))
async def handle_help(message: Message):
    """Handler for the /help command."""
    await message.answer(HELP_TEXT)


@router.message(StateFilter("*"), Command("cancel"))
async def handle_cancel(message: Message, state: FSMContext) -> None:
    """Allow user to cancel any action at any time."""
    current_state = await state.get_state()
    if current_state is None:
        return  # Nothing to cancel

    await state.clear()
    await message.answer(
        "Action canceled. To start over, use the /start command.",
        reply_markup=ReplyKeyboardRemove(),
    )


# --- PRIVATE HELPER FOR THIS MODULE ---
async def _show_summary(message: Message, state: FSMContext, edit_mode: bool = False):
    """Private helper to show summary and set state. Avoids code duplication."""
    data = await state.get_data()
    passport_data = PassportData.model_validate(data.get("passport_data"))
    vehicle_data = VehicleDocumentData.model_validate(data.get("vehicle_document_data"))
    summary_text = await get_summary_text(passport_data, vehicle_data)

    if edit_mode:
        await message.edit_text(summary_text, reply_markup=kb.document_confirm_kb)
    else:
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
    await message.answer(
        f"Hello, {message.from_user.first_name}!👋 Welcome to the insurance bot 🤖\n\n"
        f"To start, please a send photo of your passport. 🛂"
    )
    await state.set_state(Form.waiting_for_passport)


# --- 1 Passport Photo Handler ---
@router.message(Form.waiting_for_passport, F.photo)
async def handle_passport(message: Message, state: FSMContext, bot: Bot):
    """
    Processes the passport photo using Mindee and asks for confirmation
    """
    text, success, data_obj = await PhotoProcessor.process_photo(message, state, bot, "passport")
    if success and data_obj:
        await state.update_data(passport_data=data_obj.model_dump(by_alias=True), passport_confirm_text=text)
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
            await callback.message.edit_text(
                "✅ Passport data confirmed.\n\n"
                "Now, please send a photo of your vehicle document 🚗 "
                "(registration certificate or insurance policy).",
                reply_markup=None,
            )
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
        passport_confirm_text = data.get("passport_confirm_text", "No data available.")
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
            vehicle_document_data=data_obj.model_dump(by_alias=True),
            vehicle_confirm_text=text,
        )
        await message.answer(text, reply_markup=kb.document_confirm_kb)
    elif text:
        await message.answer(text)


# --- 2a. Vehicle Document Confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong", "cancel_changing"]), Form.waiting_for_vehicle_document)
async def process_vehicle_document(callback: CallbackQuery, state: FSMContext):
    """
    This function is called when the user confirms or rejects the vehicle document data.
    If the user confirms, it sends a message asking for the summary confirmation.
    If the user rejects, it asks them to send a new vehicle document photo.
    If the user chooses to cancel changing, it sends a summary of the insurance data and asks
    for confirmation.
    """

    data = await state.get_data()
    is_changing = data.get("is_changing", False)

    if callback.data == "data_ok":
        if is_changing:
            await state.update_data(is_changing=False)

            await _show_summary(callback.message, state, edit_mode=True)

            await callback.message.answer("✅ Data updated. Let's review the final summary again", show_alert=False)

        else:
            await _show_summary(callback.message, state, edit_mode=True)

    elif callback.data == "data_wrong":
        msg_with_cancel_button = await callback.message.edit_text(
            "❌ OK. Please send a new photo of your vehicle document.",
            reply_markup=kb.cancel_only_kb,
        )
        await state.update_data(msg_to_edit_id=msg_with_cancel_button.message_id)
        await state.set_state(Form.waiting_for_vehicle_document)

    elif callback.data == "cancel_changing":
        vehicle_confirm_text = data.get("vehicle_confirm_text", "No data available.")
        await callback.message.edit_text(vehicle_confirm_text, reply_markup=kb.document_confirm_kb)
        await state.set_state(Form.waiting_for_vehicle_document)

    await callback.answer()


# --- 3. Summary Confirmation ---
@router.callback_query(F.data.in_(["data_ok", "data_wrong"]), Form.waiting_for_summary_confirmation)
async def process_summary(callback: CallbackQuery, state: FSMContext):
    """
    This function is called when the user confirms or rejects the summary data.
    If the user confirms, it sends a message asking for the insurance price confirmation.
    If the user rejects, it asks them to change the photo.
    """
    data = await state.get_data()
    summary_text_message = data.get("summary_text_message", "No data available.")
    clean_text = get_clean_text(summary_text_message)

    if callback.data == "data_ok":
        await callback.message.edit_text(
            f"✅ Summary data confirmed.\n\nThe insurance price is: **{s.insurance_price} USD**. Do you agree?",
            parse_mode="Markdown",
            reply_markup=kb.confirm_kb,
        )

        await state.set_state(Form.waiting_for_price_confirmation)

    elif callback.data == "data_wrong":
        await callback.message.edit_text(
            f"{clean_text}\n\n❌ Summary data is incorrect. Choice which photo you want to change.",
            reply_markup=kb.change_photo_kb,
        )
        await state.set_state(Form.waiting_for_change_choice)
    await callback.answer()


# --- 4. Price Confirmation ---
@router.callback_query(F.data.in_(["confirm_yes", "confirm_no"]), Form.waiting_for_price_confirmation)
async def handle_price_confirmation(callback: CallbackQuery, state: FSMContext):
    """
    This function is called when the user confirms or rejects the insurance price.
    If the user confirms, it generates the insurance policy text using OpenAI and sends it to the user.
    If the user rejects, it sends a message indicating that the price is not acceptable.
    """
    if callback.data == "confirm_yes":
        await callback.message.edit_text(
            "✅ Purchase confirmed!\n\n🎨 Generating your insurance policy...",
            reply_markup=None,
        )
        data = await state.get_data()
        passport_data = PassportData.model_validate(data.get("passport_data"))
        vehicle_data = VehicleDocumentData.model_validate(data.get("vehicle_document_data"))

        policy_text = await openai_service.generate_policy_text(passport_data, vehicle_data)

        await callback.message.edit_text(
            policy_text,
            parse_mode="HTML",
        )

        await callback.message.answer("Thank you for using our service! 🎉\n\n")
        await state.clear()

    elif callback.data == "confirm_no":
        await callback.message.edit_text(
            "❌ We are sorry that the price did not suit you. This is the only available price. If you change your mind, please start over with /start.",
            reply_markup=None,
        )
        await state.clear()

    await callback.answer()


# --- Callback query handler for changing photos ---
@router.callback_query(
    F.data.in_(["change_passport", "change_vehicle_document", "cancel_changing"]),
    Form.waiting_for_change_choice,
)
async def process_change_choice(callback: CallbackQuery, state: FSMContext):
    """
    This function is called when the user chooses to change a photo or cancel the changing.
    It handles the following cases:
    1. If the user chooses to change the passport photo, it prompts them to send a new passport photo.
    2. If the user chooses to change the vehicle document photo, it prompts them to send a new vehicle document photo.
    3. If the user chooses to cancel the changing, it sends a summary of the insurance data and asks for confirmation.
    """
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


# --- CATCH-ALL HANDLER FOR UNHANDLED TEXT MESSAGES ---
@router.message(F.text)
async def handle_unhandled_text(message: Message):
    """
    Handles any text messages from the user that are not part of the main FSM flow.
    Uses OpenAI to generate a smart, conversational reply.
    """
    if message.text.startswith("/"):
        await message.answer("🚫 Sorry, I don't understand this command. Please use /start to begin.")
        return

    reply_text = await openai_service.generate_conversational_reply(message.text)
    await message.answer(reply_text)
