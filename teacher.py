import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext


def get_db_connection():
    # Replace with your actual connection details
    conn = psycopg2.connect(
        dbname="talant",
        user="postgres",
        password="postgres",
        host="91.147.92.32",
        port="5432"
    )
    return conn


async def become_teacher(update: Update, context: CallbackContext):
    # Get the user ID from the update
    user_id = update.effective_user.id

    # Get the username or other details if needed (e.g. username or first name)
    username = update.effective_user.username or update.effective_user.first_name

    # Insert the user ID into the 'teachers' table
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user is already in the teachers table (optional)
        cursor.execute("SELECT * FROM teachers WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            await update.message.reply_text("You are already registered as a teacher.")
        else:
            # Insert the new teacher into the database
            cursor.execute("INSERT INTO teachers (user_id, username) VALUES (%s, %s)", (user_id, username))
            conn.commit()
            await update.message.reply_text("You have been successfully registered as a teacher.")

        cursor.close()
        conn.close()

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

