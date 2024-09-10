import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

sections = [
    "Игра на гитаре 🎸",
    "Игра на фортепиано 🎹",
    "Шахматы ♟️",
    "Бухгалтерия 1С 💼",
    "Йога 🧘",
    "Танцы 💃",
    "Рисование 🎨",
    "Фотография 📸",
    "Кулинария 🍳"
]

addresses = [
    "Улы Дала, 43",
    "Мангилик Ел, 25",
    "Куйши Дина, 5",
    "Проспект Кабанбай Батыра, 50"
]

times = [
    "09:00-11:00",
    "11:00-13:00",
    "13:00-15:00",
    "15:00-17:00",
    "17:00-19:00",
    "19:00-21:00"
]

payment_methods = [
    "Kaspi 💳",
    "Halyk 💳"
]


async def section_selection(update: Update, context):
    # Создание кнопок с секциями
    keyboard = [
        [InlineKeyboardButton(section, callback_data=f"section_{section}")] for section in sections
    ]

    # Создание разметки с клавиатурой
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка сообщения с кнопками
    await update.message.reply_text("Выберите секцию:", reply_markup=reply_markup)


async def button_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Если пользователь выбрал секцию, показать выбор адреса
    if query.data.startswith("section_"):
        selected_section = query.data.split("_")[1]
        context.user_data['selected_section'] = selected_section  # Сохраняем выбранную секцию

        # Создание кнопок с адресами
        keyboard = [
            [InlineKeyboardButton(address, callback_data=f"address_{address}")] for address in addresses
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Вы выбрали секцию: {selected_section}\nТеперь выберите адрес, где вам будет удобно:",
            reply_markup=reply_markup
        )

    # Если пользователь выбрал адрес, показать выбор времени
    elif query.data.startswith("address_"):
        selected_address = query.data.split("_")[1]
        context.user_data['selected_address'] = selected_address  # Сохраняем выбранный адрес
        selected_section = context.user_data.get('selected_section', 'секция')

        # Создание кнопок с временем
        keyboard = [
            [InlineKeyboardButton(time, callback_data=f"time_{time}")] for time in times
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Вы выбрали секцию: {selected_section}\nАдрес: {selected_address}\nТеперь выберите время для записи:",
            reply_markup=reply_markup
        )

    # Если пользователь выбрал время, показать выбор способа оплаты
    elif query.data.startswith("time_"):
        selected_time = query.data.split("_")[1]
        context.user_data['selected_time'] = selected_time  # Сохраняем выбранное время
        selected_address = context.user_data.get('selected_address', 'адрес')
        selected_section = context.user_data.get('selected_section', 'секция')

        # Создание кнопок со способами оплаты
        keyboard = [
            [InlineKeyboardButton(method, callback_data=f"payment_{method}")] for method in payment_methods
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Вы выбрали секцию: {selected_section}\nАдрес: {selected_address}\nВремя: {selected_time}\nТеперь выберите способ оплаты:",
            reply_markup=reply_markup
        )

    # Если пользователь выбрал способ оплаты, запросить номер телефона
    elif query.data.startswith("payment_"):
        selected_payment = query.data.split("_")[1]
        context.user_data['selected_payment'] = selected_payment  # Сохраняем выбранный способ оплаты
        selected_time = context.user_data.get('selected_time', 'время')
        selected_address = context.user_data.get('selected_address', 'адрес')
        selected_section = context.user_data.get('selected_section', 'секция')

        # Создание клавиатуры для ввода номера телефона
        keyboard = [
            [KeyboardButton("Поделиться номером телефона", request_contact=True)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        # Отправка сообщения с клавиатурой для номера телефона
        await query.message.reply_text(
            f"Вы записаны на секцию '{selected_section}' по адресу: {selected_address} на {selected_time}.\nСпособ оплаты: {selected_payment}.\nПожалуйста, поделитесь своим номером телефона для завершения записи:",
            reply_markup=reply_markup
        )


# Function to handle incoming contacts
async def contact_handler(update: Update, context):
    contact = update.message.contact
    phone_number = contact.phone_number

    # Сохранение номера телефона
    context.user_data['phone_number'] = phone_number

    # Подтверждение записи
    selected_payment = context.user_data.get('selected_payment', 'способ оплаты')
    selected_time = context.user_data.get('selected_time', 'время')
    selected_address = context.user_data.get('selected_address', 'адрес')
    selected_section = context.user_data.get('selected_section', 'секция')

    # Отправка подтверждения записи
    await update.message.reply_text(
        f"Спасибо! Вы записаны на секцию '{selected_section}' по адресу: {selected_address} на {selected_time}.\nСпособ оплаты: {selected_payment}.\nВаш номер телефона: {phone_number}.\nОжидайте подтверждение записи."
    )

    # Ожидание 3 секунды
    await asyncio.sleep(3)

    # Кнопки для дальнейшего взаимодействия
    buttons = [
        [KeyboardButton("Записаться на секцию ✒️")],
        [KeyboardButton("Как пользоваться ботом 📖")],
        [KeyboardButton("Наши контакты ☎️")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    # Отправка сообщения с кнопками
    await update.message.reply_text(
        "Вы успешно записаны! 🎉\nМы рады, что вы выбрали наш курс. Если у вас есть вопросы, не стесняйтесь обращаться к нам. 😊",
        reply_markup=reply_markup
    )