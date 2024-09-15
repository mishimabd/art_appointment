import psycopg2
from psycopg2 import sql
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext


async def start_button(update: Update, context: CallbackContext) -> None:
    context.user_data["is_text_for_adding"] = False
    user = update.message.from_user

    # Save user's Telegram ID and username to the database
    save_user_to_db(user.id, user.username)

    # Define the buttons for the bot's reply
    buttons = [
        [KeyboardButton("Виртуальный ассистент 🤖")],
        [KeyboardButton("Как пользоваться ботом 📖")],
        [KeyboardButton("Очистить историю 🗑️")],  # New button for clearing history
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    # Reply with a greeting message
    await update.message.reply_text(
        f"👋Добрый день, {user.first_name}! Я ваш виртуальный ассистент! Задавайте ваши интересующие вопросы",
        reply_markup=reply_markup, parse_mode="HTML"
    )


def save_user_to_db(user_id, username):
    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="your_database_name",
            user="your_db_user",
            password="your_db_password",
            host="your_db_host",
            port="your_db_port"
        )
        cursor = conn.cursor()

        # Insert user data into the database
        insert_query = sql.SQL("""
            INSERT INTO users (telegram_id, username)
            VALUES (%s, %s)
            ON CONFLICT (telegram_id) DO NOTHING;  # Avoid duplicate entries
        """)
        cursor.execute(insert_query, (user_id, username))

        # Commit the transaction and close the connection
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving user to the database: {e}")