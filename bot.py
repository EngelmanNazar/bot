import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from database import add_user, get_all_users, init_db
from config import TOKEN 

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен (оставьте ваш)
TOKEN = "8380366880:AAGvTRPEnALZmSvXcxMaiLCwBvpLkj8yrgk"

# ВРЕМЕННО: ID админа будет определяться автоматически
ADMIN_ID = None

# Состояния для создания товара
class ProductState(StatesGroup):
    name = State()
    description = State()
    price = State()

async def main():
    init_db()
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    admin_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пользователи"), KeyboardButton(text="Создать товар"), KeyboardButton(text="Стикеры")],
            [KeyboardButton(text="/myid"), KeyboardButton(text="/setadmin")]
        ],
        resize_keyboard=True
    )

    user_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Стикеры"), KeyboardButton(text="/myid")]],
        resize_keyboard=True
    )

    stickers_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="RESPECT SIGMA MOMENT")],
            [KeyboardButton(text="ROFLS")],
            [KeyboardButton(text="Вернуться")]
        ],
        resize_keyboard=True
    )

    admin_id = None

    @dp.message(F.text == "/start")
    async def start(message: Message):
        user = message.from_user
        user_id = user.id
        add_user(user_id=user_id, username=user.username, first_name=user.first_name)
        
        nonlocal admin_id
        if admin_id is None:
            admin_id = user_id
            await message.answer(f"🎉 Вы первый пользователь! Вы назначены админом!\nВаш ID: {user_id}")
        
        if user_id == admin_id:
            await message.answer(f"👑 Привет, админ! (ID: {user_id})", reply_markup=admin_keyboard)
        else:
            await message.answer(f"👋 Привет! (ID: {user_id})", reply_markup=user_keyboard)

    @dp.message(F.text == "/myid")
    async def get_my_id(message: Message):
        user_id = message.from_user.id
        await message.answer(f"🆔 Ваш ID: `{user_id}`", parse_mode="Markdown")

    @dp.message(F.text == "/setadmin")
    async def set_admin(message: Message):
        nonlocal admin_id
        user_id = message.from_user.id
        if admin_id is None:
            admin_id = user_id
            await message.answer(f"✅ Вы назначены админом!\nВаш ID: {user_id}", reply_markup=admin_keyboard)
        elif user_id == admin_id:
            await message.answer(f"⚠️ Вы уже админ!\nID: {user_id}")
        else:
            await message.answer(f"❌ Админ уже назначен!\nТекущий админ ID: {admin_id}")

    @dp.message(F.text == "Стикеры")
    async def stickers_menu(message: Message):
        await message.answer("Выбери стикер", reply_markup=stickers_keyboard)

    @dp.message(F.text == "RESPECT SIGMA MOMENT")
    async def sticker_sigma(message: Message):
        await message.answer_sticker("CAACAgIAAxkBAAEPubloRqmRw9kFW7LK8fWDZtgwqj9yygACNhIAAs35cEjC-Ns6fJPC4zYE")

    @dp.message(F.text == "ROFLS")
    async def sticker_rofls(message: Message):
        await message.answer_sticker("CAACAgIAAxkBAAEPuZZoRqWJkG0yAAGtyDuIUtbSzd_SuOoAAvwLAAKwS6lKCrr3pTQ9ziI2BA")

    @dp.message(F.text == "Вернуться")
    async def back_to_menu(message: Message):
        nonlocal admin_id
        if message.from_user.id == admin_id:
            await message.answer("Вернулся в главное меню", reply_markup=admin_keyboard)
        else:
            await message.answer("Вернулся в главное меню", reply_markup=user_keyboard)

    @dp.message(F.text == "Пользователи")
    async def show_users(message: Message):
        nonlocal admin_id
        if admin_id is None:
            await message.answer("⚠️ Админ еще не назначен. Используйте /setadmin")
            return
        if message.from_user.id != admin_id:
            await message.answer("⛔ У вас нет прав для просмотра пользователей")
            return
        users = get_all_users()
        if not users:
            await message.answer("📭 В базе данных пока нет пользователей")
            return
        text = "👥 Пользователи бота:\n\n"
        for i, (user_id, username, first_name) in enumerate(users, 1):
            username = username if username else "Нет юзернейма"
            first_name = first_name if first_name else "Без имени"
            admin_flag = " 👑" if user_id == admin_id else ""
            text += f"{i}. {first_name} | @{username} | ID: {user_id}{admin_flag}\n"
        await message.answer(text)

    @dp.message(F.text == "Создать товар")
    async def add_product_start(message: Message, state: FSMContext):
        nonlocal admin_id
        if admin_id is None:
            await message.answer("⚠️ Админ еще не назначен. Используйте /setadmin")
            return
        if message.from_user.id != admin_id:
            await message.answer("⛔ У вас нет прав для создания товаров")
            return
        await message.answer("📝 Введите название товара:")
        await state.set_state(ProductState.name)

    @dp.message(ProductState.name)
    async def add_product_name(message: Message, state: FSMContext):
        await state.update_data(name=message.text)
        await message.answer("📄 Введите описание товара:")
        await state.set_state(ProductState.description)

    @dp.message(ProductState.description)
    async def add_product_description(message: Message, state: FSMContext):
        await state.update_data(description=message.text)
        await message.answer("💰 Введите цену товара (только цифры):")
        await state.set_state(ProductState.price)

    @dp.message(ProductState.price)
    async def add_product_price(message: Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer("❌ Цена должна быть числом! Введите еще раз:")
            return
        data = await state.get_data()
        price = int(message.text)
        await message.answer(f"✅ Товар создан!\nНазвание: {data['name']}\nОписание: {data['description']}\nЦена: {price} руб.")
        await state.clear()

    try:
        print("🤖 Бот запускается...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())