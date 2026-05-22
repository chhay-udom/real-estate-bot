import logging
import mysql.connector
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters,
)

# 1. ការកំណត់ Flask សម្រាប់ Render Health Check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. ការកំណត់ Telegram Bot
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

CHOOSING_TYPE, CHOOSING_LOCATION, CHOOSING_BUDGET, CHOOSING_PAYMENT, GETTING_NAME, GETTING_PHONE = range(6)
AGENT_CHAT_ID = "-4998273283"
TOKEN = "8771495453:AAGXJiAcSrYL23HsWoDIutJk-S4e6GWJics"

def get_db_connection():
    return mysql.connector.connect(
        host="mysql-3d44dfd3-bot-project.i.aivencloud.com",
        user="avnadmin",
        password="AVNS_i6gzgyV5-18ereaucCB",
        port=25516,
        database="defaultdb",
        ssl_disabled=True
    )

# --- Functions របស់ Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("🏠 ផ្ទះបុរី", callback_data="Borey")], [InlineKeyboardButton("🏢 Condo", callback_data="Condo")], [InlineKeyboardButton("🌍 ដីលក់", callback_data="Land")]]
    await update.message.reply_text("សួស្តី 👋 សូមជ្រើសរើសសេវាកម្ម:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_TYPE

async def handle_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['property_type'] = query.data
    keyboard = [[InlineKeyboardButton("📍 ភ្នំពេញ", callback_data="Phnom_Penh")], [InlineKeyboardButton("📍 ខេត្តសៀមរាប", callback_data="Siem_Reap")], [InlineKeyboardButton("📍 ខេត្តបាត់ដំបង", callback_data="Battambang")]]
    await query.edit_message_text(text="តើលោកអ្នកចង់ស្វែងរកអចលនទ្រព្យនៅក្នុងតំបន់ណាដែរ?", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_LOCATION

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['location'] = query.data
    keyboard = [[InlineKeyboardButton("ក្រោម $៥ ម៉ឺន", callback_data="under_50k")], [InlineKeyboardButton("$៥ ម៉ឺន - $១០ ម៉ឺន", callback_data="50k_100k")], [InlineKeyboardButton("$១០ ម៉ឺន - $២០ ម៉ឺន", callback_data="100k_200k")], [InlineKeyboardButton("លើសពី $២០ ម៉ឺន", callback_data="above_200k")]]
    await query.edit_message_text(text="តើកញ្ចប់ថវិកាប្រហែលប៉ុន្មានដែរ?", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_BUDGET

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['budget'] = query.data
    keyboard = [[InlineKeyboardButton("ទិញដាច់ (Cash)", callback_data="Cash")], [InlineKeyboardButton("បង់រំលស់ (Installment)", callback_data="Installment")]]
    await query.edit_message_text(text="តើលោកអ្នកមានបំណងទិញដាច់ ឬចង់បង់រំលស់ដែរ?", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_PAYMENT

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['payment_method'] = query.data
    await query.edit_message_text(text="សូមបញ្ចូលឈ្មោះរបស់អ្នក៖")
    return GETTING_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['customer_name'] = update.message.text
    contact_keyboard = [[{"text": "📱 ចែករំលែកលេខទូរស័ព្ទ", "request_contact": True}]]
    await update.message.reply_text("សូមបញ្ចូលលេខទូរស័ព្ទ៖", reply_markup=ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GETTING_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    first_name = context.user_data.get('customer_name')
    # បញ្ចូលទិន្នន័យ Database
    try:
        db = get_db_connection()
        cursor = db.cursor()
        sql = "INSERT INTO leads (customer_name, phone_number, property_type, location, budget, payment_method) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (first_name, phone_number, context.user_data.get('property_type'), context.user_data.get('location'), context.user_data.get('budget'), context.user_data.get('payment_method'))
        cursor.execute(sql, val)
        db.commit()
        db.close()
    except Exception as e:
        print(f"DB Error: {e}")
    await update.message.reply_text("អរគុណ! ភ្នាក់ងារនឹងទាក់ទងលោកអ្នកក្នុងពេលឆាប់ៗ។", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("បោះបង់ការសាកសួរ។", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def run_bot():
    bot_app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_TYPE: [CallbackQueryHandler(handle_type)],
            CHOOSING_LOCATION: [CallbackQueryHandler(handle_location)],
            CHOOSING_BUDGET: [CallbackQueryHandler(handle_budget)],
            CHOOSING_PAYMENT: [CallbackQueryHandler(handle_payment)],
            GETTING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            GETTING_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, handle_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    bot_app.add_handler(conv_handler)
    print("Bot is running with polling...")
    bot_app.run_polling()

if __name__ == "__main__":
    # រត់ Flask និង Bot ស្របគ្នា
    threading.Thread(target=run_flask).start()
    run_bot()