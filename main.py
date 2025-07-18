import os
import csv
import logging
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "users.csv"

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_button = KeyboardButton("📱 Kontakt yuborish", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Assalomu alaykum! Ovoz berish uchun kontakt raqamingizni yuboring 👇", reply_markup=reply_markup)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        user_id = update.message.from_user.id
        user_states[user_id] = {
            "phone_number": contact.phone_number,
            "name": update.message.from_user.full_name,
            "username": update.message.from_user.username or "",
            "step": "code"
        }
        await update.message.reply_text("SMS kodni kiriting (kodni shartli kiriting, bu demo versiya).")
    else:
        await update.message.reply_text("Iltimos, kontaktni to‘g‘ri yuboring.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id, {})

    if state.get("step") == "code":
        state["code"] = text
        state["step"] = "voted"
        with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([user_id, state["name"], state["username"], state["phone_number"], state["code"]])
        await update.message.reply_text("✅ Ovoz berishingiz muvaffaqiyatli qabul qilindi!")
    else:
        await update.message.reply_text("Boshlash uchun /start buyrug‘ini yuboring.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()