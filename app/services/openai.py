from openai import AsyncOpenAI

from app.config import s
from app.models import PassportData, VehicleDocumentData


class OpenAIService:
    def __init__(self, api_key, model: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model

    async def generate_policy_text(self, passport: PassportData, vehicle: VehicleDocumentData):
        """Generates a dummy insurance policy text using OpenAI."""
        system_prompt = (
            "You are an automated system that generates car insurance policies in simple HTML format for a Telegram bot. "
            "Your task is to generate ONLY the HTML body of the policy. "
            "Use HTML tags like <b> for bold and <i> for italic. "
            "Your output MUST start with '📜 <b>Car Insurance Policy</b>'. "
            "DO NOT include any other text, greetings, explanations, or comments before or after the policy. "
            "Use emojis like 👤, 🚗, 🏢, 📅, 🛡️, 📞 for visual appeal."
        )

        user_prompt = (
            f"<b>Policyholder Information:</b>\n"
            f"  - <b>Full Name:</b> {passport.given_names} {passport.surnames}\n"
            f"  - <b>Passport Number:</b> {passport.passport_number}\n\n"
            f"<b>Vehicle Information:</b>\n"
            f"  - <b>Vehicle Model:</b> {vehicle.model}\n"
            f"  - <b>VIN:</b> {vehicle.vin}\n"
            f"  - <b>Registration Number:</b> {vehicle.reg_number}\n\n"
            f"<b>Provider:</b> AutoInsure_bot\n"
            f"<b>Validity:</b> <i>1 year from today</i>\n\n"
            f"<b>Coverage Details:</b>\n"
            f"  - Liability, Collision, Comprehensive, Medical, Uninsured Motorist\n\n"
            f"<b>Contact:</b>\n"
            f"  - Customer Service: 1-800-555-0199\n"
            f"  - Email: support@autoinsure.com"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                max_tokens=500,
                temperature=0.4,
            )
            policy_content = response.choices[0].message.content
            safe_content = policy_content.replace("<br>", "\n").replace("<br/>", "\n")
            safe_content = safe_content.replace("<div>", "").replace("</div>", "")
            return safe_content.strip()

        except Exception as e:
            print(f"Error generating policy text: {e}")
            return "An error occurred while generating the policy text. Please try again later."

    async def generate_conversational_reply(self, user_message: str) -> str:
        """Generates a conversational reply for unhandled user messages."""

        system_prompt = (
            "You are AutoInsure, the virtual assistant of the AutoInsure Telegram bot, designed to help users purchase car insurance step by step. "
            "Always keep the conversation strictly focused on the car insurance process: collecting passport and vehicle documents, showing extracted data, confirming correctness, and finalizing the policy. "
            "If a user seems lost, says hello, or asks for help, briefly explain the current step or suggest sending /start to begin again. "
            "Politely refuse to discuss anything not related to car insurance or the current process. "
            "Keep all replies short, friendly, and in the user's language. "
            "Never answer general, personal, or off-topic questions. "
            "If the user asks about price, always state the fixed price is 100 USD. "
            "If all required data is collected and confirmed, generate a simple, friendly insurance policy text using provided details."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                max_tokens=100,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in conversational reply: {e}")
            return "I'm having a little trouble right now. Please try starting over with /start."


openai_service = OpenAIService(
    s.openai_api_key,
    s.openai_model,
)
