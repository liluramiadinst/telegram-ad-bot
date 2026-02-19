import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    link = State()
    product = State()

def subscribe_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")
    kb.button(text="Я подписался", callback_data="check")
    kb.adjust(1)
    return kb.as_markup()

async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member","administrator","creator"]
    except:
        return False

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    ok = await check_sub(message.from_user.id)
    if not ok:
        await message.answer("Чтобы отправить заявку на рекламу, сначала подпишитесь на мой канал:", reply_markup=subscribe_kb())
        return
    await message.answer("Как вас зовут или ник?")
    await state.set_state(Form.name)

@dp.callback_query(lambda c: c.data=="check")
async def recheck(call: CallbackQuery, state: FSMContext):
    ok = await check_sub(call.from_user.id)
    if not ok:
        await call.answer("Я всё ещё не вижу подписку 🙂", show_alert=True)
        return
    await call.message.answer("Отлично. Как вас зовут или ник?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Ссылка на проект / магазин / аккаунт?")
    await state.set_state(Form.link)

@dp.message(Form.link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("Что именно вы хотите прорекламировать?")
    await state.set_state(Form.product)

@dp.message(Form.product)
async def get_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    data = await state.get_data()

    text = f"""Новая заявка на рекламу

Имя: {data['name']}
Ссылка: {data['link']}
Что рекламируют: {data['product']}
Telegram: @{message.from_user.username} (id {message.from_user.id})
"""

    await bot.send_message(ADMIN_CHAT_ID, text)
    await message.answer("Спасибо! Я посмотрю заявку и свяжусь с вами.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
