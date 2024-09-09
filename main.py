from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from art_buttons import start_button
from contacts import our_contacts

TELEGRAM_BOT_TOKEN = "7440105099:AAHnLcnOsseDfqWH_F0codMl80TN1o3gmAQ"

def main():
    print(f"{datetime.now()} - Started")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_button))
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("^(Наши контакты ☎️)$"), our_contacts))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
