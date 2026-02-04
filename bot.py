import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup

from database import add_user, get_all_users, init_db



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8380366880:AAGvTRPEnALZmSvXcxMaiLCwBvpLkj8yrgk"
ADMIN_ID =  6864170180  

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
            [
                KeyboardButton(text="Пользователи"),
                KeyboardButton(text="Создать товар"),
                KeyboardButton(text="Стикеры")
            ],
            [
                KeyboardButton(text="/id"),  # Добавили кнопку для проверки ID
                KeyboardButton(text="/admin")  # Добавили кнопку для проверки админки
            ]
        ],
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


    @dp.message(F.text == "/start")
    async def start(message: Message):
        user = message.from_user
        user_id = user.id
        
        add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name
        )
        
        await message.answer(f"Ваш ID: `{user_id}`\n"
                            f"ID админа в настройках: `{ADMIN_ID}`",
                            parse_mode="Markdown")
        
        if user_id == ADMIN_ID:
            await message.answer("✅ Вы админ! Привет, админ 👑", reply_markup=admin_keyboard)
        else:
            await message.answer("👋 Привет! Бот запущен.", reply_markup=admin_keyboard)


    @dp.message(F.text == "/id")
    async def get_my_id(message: Message):
        user_id = message.from_user.id
        await message.answer(f"Ваш ID: `{user_id}`\n\n"
                            f"Имя: {message.from_user.first_name}\n"
                            f"Юзернейм: @{message.from_user.username}", 
                            parse_mode="Markdown")

    @dp.message(F.text == "/admin")
    async def check_admin(message: Message):
        user_id = message.from_user.id
        is_admin = user_id == ADMIN_ID
        
        await message.answer(
            f"📊 Статус проверки:\n"
            f"• Ваш ID: `{user_id}`\n"
            f"• ID админа в настройках: `{ADMIN_ID}`\n"
            f"• Вы админ: {'✅ ДА' if is_admin else '❌ НЕТ'}\n\n"
            f"{'🎉 Поздравляем! У вас есть права админа!' if is_admin else '⚠️ У вас нет прав админа'}",
            parse_mode="Markdown"
        )


    @dp.message(F.text == "Стикеры")
    async def stickers_menu(message: Message):
        await message.answer("Выбери стикер", reply_markup=stickers_keyboard)

    @dp.message(F.text == "RESPECT SIGMA MOMENT")
    async def sticker_sigma(message: Message):
        await message.answer_sticker(
            "CAACAgIAAxkBAAEPubloRqmRw9kFW7LK8fWDZtgwqj9yygACNhIAAs35cEjC-Ns6fJPC4zYE"
        )

    @dp.message(F.text == "ROFLS")
    async def sticker_rofls(message: Message):
        await message.answer_sticker(
            "CAACAgIAAxkBAAEPuZZoRqWJkG0yAAGtyDuIUtbSzd_SuOoAAvwLAAKwS6lKCrr3pTQ9ziI2BA"
        )

    @dp.message(F.text == "Вернуться")
    async def back_to_menu(message: Message):
        await message.answer("Вернулся в главное меню", reply_markup=admin_keyboard)


    @dp.message(F.text == "Пользователи")
    async def show_users(message: Message):
        if message.from_user.id != ADMIN_ID:
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
            text += f"{i}. {first_name} | @{username} | ID: {user_id}\n"

        await message.answer(text)


    @dp.message(F.text == "Создать товар")
    async def add_product_start(message: Message, state: FSMContext):
        if message.from_user.id != ADMIN_ID:
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

        await message.answer(
            f"✅ Товар успешно создан!\n\n"
            f"📦 Название: {data['name']}\n"
            f"📝 Описание: {data['description']}\n"
            f"💰 Цена: {price} руб.\n\n"
            f"Товар сохранен в системе.",
            reply_markup=admin_keyboard
        )
        await state.clear()


    @dp.message(F.text.lower().in_(["отмена", "cancel", "стоп"]))
    async def cancel_handler(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
            await message.answer("❌ Действие отменено", reply_markup=admin_keyboard)


    @dp.message()
    async def unknown_command(message: Message):
        await message.answer(
            "🤔 Я не понял команду. Используйте кнопки или команды:\n"
            "/start - Перезапустить бота\n"
            "/id - Узнать свой ID\n"
            "/admin - Проверить права админа",
            reply_markup=admin_keyboard
        )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    print("🤖 Бот запускается...")
    asyncio.run(main())