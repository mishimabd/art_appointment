import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Application
import asyncpg

payment_methods = [
    "Kaspi 💳",
    "Halyk 💳"
]


async def fetch_sections_from_db():
    conn = await asyncpg.connect(user='postgres', password='Lg26y0M@x',
                                 database='talant', host='91.147.92.32')
    sections = await conn.fetch("SELECT name, free_times, address FROM sections")
    await conn.close()
    return sections


async def section_selection(update: Update, context: CallbackContext):
    sections_data = await fetch_sections_from_db()

    keyboard = [
        [InlineKeyboardButton(section['name'], callback_data=f"section_{section['name']}")]
        for section in sections_data
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите секцию:", reply_markup=reply_markup)


async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("section_"):
        selected_section_name = query.data.split("_")[1]
        context.user_data['selected_section'] = selected_section_name

        conn = await asyncpg.connect(user='postgres', password='postgres',
                                     database='talant', host='91.147.92.32')
        section_data = await conn.fetchrow("SELECT address, free_times FROM sections WHERE name=$1",
                                           selected_section_name)
        await conn.close()

        if section_data:
            addresses = section_data['address']
            times = section_data['free_times']
            context.user_data['times'] = times  # Store times for later use

            keyboard = [
                [InlineKeyboardButton(address, callback_data=f"address_{address}")] for address in addresses
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Вы выбрали секцию: {selected_section_name}\nТеперь выберите адрес, где вам будет удобно:",
                reply_markup=reply_markup
            )

    elif query.data.startswith("address_"):
        selected_address = query.data.split("_")[1]
        context.user_data['selected_address'] = selected_address
        selected_section = context.user_data.get('selected_section', 'секция')

        times = context.user_data.get('times', [])  # Retrieve times from user data
        keyboard = [
            [InlineKeyboardButton(time, callback_data=f"time_{time}")] for time in times
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Вы выбрали секцию: {selected_section}\nАдрес: {selected_address}\nТеперь выберите время для записи:",
            reply_markup=reply_markup
        )

    elif query.data.startswith("time_"):
        selected_time = query.data.split("_")[1]
        context.user_data['selected_time'] = selected_time
        selected_address = context.user_data.get('selected_address', 'адрес')
        selected_section = context.user_data.get('selected_section', 'секция')

        keyboard = [
            [InlineKeyboardButton(method, callback_data=f"payment_{method}")] for method in payment_methods
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Вы выбрали секцию: {selected_section}\nАдрес: {selected_address}\nВремя: {selected_time}\nТеперь выберите способ оплаты:",
            reply_markup=reply_markup
        )

    elif query.data.startswith("payment_"):
        selected_payment = query.data.split("_")[1]
        context.user_data['selected_payment'] = selected_payment
        selected_time = context.user_data.get('selected_time', 'время')
        selected_address = context.user_data.get('selected_address', 'адрес')
        selected_section = context.user_data.get('selected_section', 'секция')

        keyboard = [
            [KeyboardButton("Поделиться номером телефона", request_contact=True)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await query.message.reply_text(
            f"Вы записаны на секцию '{selected_section}' по адресу: {selected_address} на {selected_time}.\nСпособ оплаты: {selected_payment}.\nПожалуйста, поделитесь своим номером телефона для завершения записи:",
            reply_markup=reply_markup
        )


async def contact_handler(update: Update, context: CallbackContext):
    contact = update.message.contact
    phone_number = contact.phone_number
    student_user_id = update.message.from_user.id  # Get the user ID of the student
    student_name = update.message.from_user.first_name  # Get the student's first name

    selected_payment = context.user_data.get('selected_payment', 'способ оплаты')
    selected_time = context.user_data.get('selected_time', 'время')
    selected_address = context.user_data.get('selected_address', 'адрес')
    selected_section = context.user_data.get('selected_section', 'секция')

    # Build the confirmation message
    confirmation_message = (
        f"Спасибо! Вы записаны на секцию '{selected_section}' по адресу: {selected_address} на {selected_time}.\n"
        f"Способ оплаты: {selected_payment}.\nВаш номер телефона: {phone_number}.\nОжидайте подтверждение записи."
    )

    # Connect to the database
    conn = await asyncpg.connect(user='postgres', password='postgres',
                                 database='talant', host='91.147.92.32')

    # Fetch the teacher_id and user_id of the teacher from the sections and teachers tables
    section_data = await conn.fetchrow("SELECT teacher_id FROM sections WHERE name=$1",
                                       selected_section)
    teacher_id = section_data['teacher_id'] if section_data else None

    # Insert the application data into the application table
    await conn.execute("""
        INSERT INTO applications (message, teacher_id, timestamp)
        VALUES ($1, $2, $3)
    """, confirmation_message, teacher_id, datetime.now())

    # Close the database connection
    await conn.close()

    # Send confirmation message to user (student)
    await update.message.reply_text(confirmation_message)

    # Notify the teacher about the new application
    if teacher_id:
        # Create a hyperlink to the student's chat
        chat_link = f"<a href='tg://user?id={student_user_id}'>{student_name}</a>"
        teacher_notification = (
            f"Новая заявка на секцию '{selected_section}' по адресу {selected_address} на время {selected_time}.\n"
            f"Студент: {chat_link} (ID: {student_user_id}).\n"
            f"Способ оплаты: {selected_payment}.\nНомер телефона студента: {phone_number}."
        )
        await context.bot.send_message(chat_id=teacher_id, text=teacher_notification, parse_mode='HTML')

    # Provide additional options to the student
    await asyncio.sleep(3)

    buttons = [
        [KeyboardButton("Записаться на секцию ✒️")],
        [KeyboardButton("Как пользоваться ботом 📖")],
        [KeyboardButton("Наши контакты ☎️")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    await update.message.reply_text(
        "Вы успешно записаны! 🎉\nМы рады, что вы выбрали наш курс. Если у вас есть вопросы, не стесняйтесь обращаться к нам. 😊",
        reply_markup=reply_markup
    )
