import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Contact
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BotCommand
import asyncio
from aiogram.client.default import DefaultBotProperties


API_TOKEN = '77493933718:AAE8nzkirH0j1qKkz3k7Dywe6YBjXsHtEzA'
ADMIN_ID = 6203004464

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot va storage
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Holatlar
class Form(StatesGroup):
    name = State()
    location = State()
    phone = State()

# Bot komandalarini belgilash (optional)
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Boshlash"),
    ]
    await bot.set_my_commands(commands)

# /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("👋 Assalomu alaykum!\nIsmingizni yozib yuboring, iltimos:")

# Ismni olish
@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.location)
    await message.answer("🌍 Siz qaysi hududdansiz? (Viloyat/Shahar nomini yozing):")

# Joylashuvni olish
@router.message(Form.location)
async def process_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await state.set_state(Form.phone)
    await message.answer("📞 Telefon raqamingizni yuborish uchun quyidagi tugmani bosing:", reply_markup=keyboard)

# Telefon raqam (to'g'ri)
@router.message(Form.phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()

    # Foydalanuvchiga javob
    await message.answer("✅ Ma'lumotlaringiz qabul qilindi:\n\n", reply_markup=ReplyKeyboardRemove())

    # Adminga yuborish
    admin_text = (
        "📥 <b>Yangi murojaat:</b>\n\n"
        f"👤 Ism: {data['name']}\n"
        f"🌍 Joylashuv: {data['location']}\n"
        f"📞 Telefon raqami: {data['phone']}"
    )
    await bot.send_message(ADMIN_ID, admin_text)

    # State tugatish
    await state.clear()

# Telefon raqam noto‘g‘ri ko‘rinishda yuborilsa
@router.message(Form.phone)
async def error_phone(message: Message):
    await message.answer("❗️Iltimos, kontakt tugmasini bosib, telefon raqamingizni yuboring.")

# Botni ishga tushuruvchi asosiy funksiya
async def main():
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
