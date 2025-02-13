import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = "7189634436:AAG141m-S07KrFfLoKvSw0tBEDE5BT-JbWU"
ADMIN_IDS = {799927457}  # آیدی عددی ادمین‌ها اینجا قرار بدید

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ذخیره وضعیت کاربران
user_data = {}


# **دریافت پیام از کاربران و ارسال به ادمین‌ها**
@dp.message()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"

    # نادیده گرفتن پیام‌های ادمین‌ها
    if user_id in ADMIN_IDS:
        return

    # چک کردن بلاک بودن کاربر
    if user_id in user_data and user_data[user_id].get("blocked", False):
        await message.answer("⛔ شما توسط ادمین بلاک شده‌اید و نمی‌توانید پیام ارسال کنید.")
        return

    # دکمه مدیریت پیام
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔧 پنل مدیریت", callback_data=f"manage_{user_id}")]
        ]
    )

    # ارسال پیام به ادمین‌ها
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"📩 پیام جدید از <b>{user_name}</b> ({user_username} - <code>{user_id}</code>):\n\n"
            f"{message.text}",
            reply_markup=keyboard
        )

    await message.answer("✅ پیام شما برای ادمین ارسال شد.")


# **پنل مدیریت پیام**
@dp.callback_query(lambda c: c.data.startswith("manage_"))
async def manage_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])

    # دکمه‌های پنل مدیریت
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ اطلاعات کاربر", callback_data=f"info_{user_id}")],
            [InlineKeyboardButton(text="🚫 بلاک کاربر", callback_data=f"block_{user_id}")],
            [InlineKeyboardButton(text="✅ آنبلاک کاربر", callback_data=f"unblock_{user_id}")],
            [InlineKeyboardButton(text="⭐ افزودن به ادمین‌ها", callback_data=f"addadmin_{user_id}")],
            [InlineKeyboardButton(text="🚷 حذف از ادمین‌ها", callback_data=f"removeadmin_{user_id}")],
            [InlineKeyboardButton(text="💬 پاسخ به کاربر", callback_data=f"reply_{user_id}")],
            [InlineKeyboardButton(text="🔓 باز کردن پروفایل کاربر", callback_data=f"openchat_{user_id}")]
        ]
    )

    await call.message.edit_text(f"🔧 پنل مدیریت برای کاربر <code>{user_id}</code>", reply_markup=keyboard)


# **دریافت اطلاعات کاربر**
@dp.callback_query(lambda c: c.data.startswith("info_"))
async def user_info(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    user_info = user_data.get(user_id, {})

    text = (
        f"ℹ️ اطلاعات کاربر:\n"
        f"👤 آیدی عددی: <code>{user_id}</code>\n"
        f"🚫 بلاک شده: {'✅ بله' if user_info.get('blocked', False) else '❌ خیر'}"
    )

    await call.message.answer(text)


# **بلاک کردن کاربر**
@dp.callback_query(lambda c: c.data.startswith("block_"))
async def block_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    user_data.setdefault(user_id, {})["blocked"] = True
    await call.message.answer(f"🚫 کاربر <code>{user_id}</code> بلاک شد و دیگر نمی‌تواند پیام دهد.")


# **آنبلاک کردن کاربر**
@dp.callback_query(lambda c: c.data.startswith("unblock_"))
async def unblock_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    user_data.setdefault(user_id, {})["blocked"] = False
    await call.message.answer(f"✅ کاربر <code>{user_id}</code> آنبلاک شد و می‌تواند پیام ارسال کند.")


# **افزودن ادمین جدید**
@dp.callback_query(lambda c: c.data.startswith("addadmin_"))
async def add_admin(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    ADMIN_IDS.add(user_id)
    await call.message.answer(f"⭐ کاربر <code>{user_id}</code> به لیست ادمین‌ها اضافه شد.")


# **حذف از ادمین‌ها**
@dp.callback_query(lambda c: c.data.startswith("removeadmin_"))
async def remove_admin(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    if user_id in ADMIN_IDS:
        ADMIN_IDS.remove(user_id)
        await call.message.answer(f"🚷 کاربر <code>{user_id}</code> از لیست ادمین‌ها حذف شد.")
    else:
        await call.message.answer(f"❌ این کاربر قبلاً ادمین نبوده است.")


# **پاسخ به کاربر**
@dp.callback_query(lambda c: c.data.startswith("reply_"))
async def reply_to_user(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await call.message.answer("لطفاً پیام خود را برای کاربر وارد کنید:")

    # ذخیره وضعیت پاسخ ادمین
    user_data[user_id] = {"waiting_for_reply": True}
    user_data[user_id]["waiting_for_reply_callback"] = call.message.message_id


# **دریافت پیام پاسخ به کاربر**
@dp.message()
async def process_reply(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return  # فقط ادمین‌ها می‌تونن جواب بدن

    for user_id, data in user_data.items():
        if data.get("waiting_for_reply", False):
            user_data[user_id]["waiting_for_reply"] = False
            await bot.send_message(user_id, f"💬 پاسخ ادمین: {message.text}")
            await message.answer(f"✅ پاسخ شما برای کاربر <code>{user_id}</code> ارسال شد.")

# **باز کردن پروفایل کاربر**
@dp.callback_query(lambda c: c.data.startswith("openchat_"))
async def open_chat(call: types.CallbackQuery):
    user_id = int(call.data.split("_")[1])
    await bot.send_message(user_id, "💬 پیام از ادمین:\nسلام، چگونه می‌توانم کمک کنم؟")
    await call.message.answer(f"🔓 پیوی کاربر <code>{user_id}</code> باز شد.")

# **دریافت پیام /start و ارسال پیام خوش‌آمدگویی**
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 سلام! لطفاً پیامت رو ارسال کن تا به ادمین‌ها برسونم.")


# **اجرای ربات**
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())