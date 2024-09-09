from telegram import Update


async def our_contacts(update: Update, context) -> None:
    our_contacts = (
        "✨ Вот наши контактные данные:\n\n"
        "📞 <b>Телефон:</b> +7 (123) 456-78-90\n"
        "✉️ <b>Email:</b> <a href='mailto:support@talant.com'>support@talant.com</a>\n\n"
        "Мы всегда готовы помочь вам с любыми вопросами или предложениями! 😊"
    )
    await update.message.reply_text(our_contacts, parse_mode="HTML")
