from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext


async def start_button(update: Update, context: CallbackContext) -> None:
    context.user_data["is_text_for_adding"] = False
    user = update.message.from_user
    buttons = [
        [KeyboardButton("Записаться на секцию ✒️")],
        [KeyboardButton("Как пользоваться ботом 📖")],
        [KeyboardButton("Наши контакты ☎️")],
        [KeyboardButton("Стать учителем 🧑‍🏫")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        f"👋Добрый день, {user.first_name}! Я телеграм бот Talant, выберите что вам интересно:",
        reply_markup=reply_markup, parse_mode="HTML"
    )
