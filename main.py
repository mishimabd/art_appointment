from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from art_buttons import start_button
from contacts import our_contacts, how_to_use
from sections import section_selection, button_click, contact_handler

TELEGRAM_BOT_TOKEN = "7440105099:AAHnLcnOsseDfqWH_F0codMl80TN1o3gmAQ"


def main():
    print(f"{datetime.now()} - Started")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_button))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Наши контакты ☎️)$"), our_contacts))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Как пользоваться ботом 📖)$"), how_to_use))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Записаться на секцию ✒️)$"), section_selection))

    application.add_handler(CallbackQueryHandler(button_click))

    application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
