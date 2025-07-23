from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --- Inline keyboard markup for various confirmation prompts ---
confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes", callback_data="confirm_yes")],
        [InlineKeyboardButton(text="❌ No", callback_data="confirm_no")],
    ]
)

# --- Inline keyboard markup for document confirmation ---
document_confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ That's correct", callback_data="data_ok")],
        [InlineKeyboardButton(text="❌ Change photo", callback_data="data_wrong")],
    ]
)


# --- Inline keyboard markup for changing photos ---
change_photo_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🛂 Change passport", callback_data="change_passport"),
            InlineKeyboardButton(text="🚗 Change vehicle document", callback_data="change_vehicle_document"),
        ],
        [InlineKeyboardButton(text="⬅ Cancel changing", callback_data="cancel_changing")],
    ]
)


# --- Inline keyboard markup for canceling changes ---
cancel_only_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="⬅ Cancel changing", callback_data="cancel_changing")]]
)
