import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

# IMPORTANT: don't leave the token as a stray line in the file.
# Use env var BOT_TOKEN instead.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Your Railway domain (server.py)
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://web-production-fafa.up.railway.app").rstrip("/")

COURSES = {
    "basic": {
        "title": "Курс «ПРОСТО О ГЛАВНОМ»",
        "old": "120",
        "new": "20",
        "details": (
            "• 5 блоков обучения по Старшим Арканам\n"
            "• 3 блока практики\n"
            "• Доступ на 90 дней\n\n"
            "После прохождения курса вы сможете сразу самостоятельно делать первые расклады"
        ),
    },
    "basic_vip": {
        "title": "Курс «ПРОСТО О ГЛАВНОМ VIP»",
        "old": "150",
        "new": "30",
        "details": (
            "• 5 блоков обучения по Старшим Арканам\n"
            "• 3 блока практики\n"
            "• 3 блока практических занятий с обратной связью\n"
            "• Доступ неограничен по времени\n\n"
            "После прохождения курса вы можете сразу начать делать первые расклады"
        ),
    },
    "steps": {
        "title": "Курс «ТАРО — ПЕРВЫЕ ШАГИ»",
        "old": "200",
        "new": "40",
        "details": (
            "• 8 блоков обучения\n"
            "• 3 блока практики\n"
            "• 3 бонусных блока практики по Старшим Арканам\n"
            "• Доступ на 90 дней\n\n"
            "После прохождения курса вы можете сразу начать делать первые расклады"
        ),
    },
    "steps_vip": {
        "title": "Курс «ТАРО — ПЕРВЫЕ ШАГИ VIP»",
        "old": "250",
        "new": "50",
        "details": (
            "• 8 блоков обучения\n"
            "• 6 блоков практики\n"
            "• 3 практических занятия с обратной связью\n\n"
            "После прохождения курса вы можете сразу начать делать первые расклады"
        ),
    },
}


def course_list_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 ПРОСТО О ГЛАВНОМ", callback_data="course_basic")],
        [InlineKeyboardButton("📕 ПРОСТО О ГЛАВНОМ VIP", callback_data="course_basic_vip")],
        [InlineKeyboardButton("📗 ТАРО — ПЕРВЫЕ ШАГИ", callback_data="course_steps")],
        [InlineKeyboardButton("📙 ТАРО — ПЕРВЫЕ ШАГИ VIP", callback_data="course_steps_vip")],
    ])


def course_detail_text(key: str) -> str:
    c = COURSES[key]
    return (
        f"🔮 <b>{c['title']}</b>\n\n"
        f"Стоимость: ❌ <s>{c['old']}€</s> / ✅ <b>{c['new']}€</b>\n\n"
        f"{c['details']}\n\n"
        "Нажмите кнопку ниже, чтобы перейти к оплате."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔮 Курс по Таро\n\nВыберите интересующий курс ниже:"
    await update.message.reply_text(text, reply_markup=course_list_keyboard())


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("course_"):
        key = data.split("course_")[1]
        text = course_detail_text(key)

        # IMPORTANT:
        # We no longer use static Stripe Payment Links or /getlink.
        # We send the user to our Railway server which creates a Checkout Session
        # with metadata {course_key, telegram_user_id}. The webhook will DM the invite automatically.
        pay_url = f"{PUBLIC_BASE_URL}/stripe/create-checkout?course={key}&tg={query.from_user.id}"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Оплатить (Stripe)", url=pay_url)],
            [InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_list")],
        ])
        await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "back_to_list":
        await query.edit_message_text(
            text="🔮 Курс по Таро\n\nВыберите интересующий курс ниже:",
            reply_markup=course_list_keyboard()
        )
        return


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("Bot is running...")
app.run_polling()
