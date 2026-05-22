import logging
import mysql.connector
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters,
)

# កំណត់ការបង្ហាញ Log
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

CHOOSING_TYPE, CHOOSING_LOCATION, CHOOSING_BUDGET, CHOOSING_PAYMENT, GETTING_NAME, GETTING_PHONE = range(6)
AGENT_CHAT_ID = "-4998273283"
TOKEN = "8771495453:AAGXJiAcSrYL23HsWoDIutJk-S4e6GWJics"
WEBHOOK_URL = "https://real-estate-bot-7drd.onrender.com"

def get_db_connection():
    return mysql.connector.connect(
        host="mysql-3d44dfd3-bot-project.i.aivencloud.com",
        user="avnadmin",
        password="AVNS_i6gzgyV5-18ereaucCB",
        port=25516,
        database="defaultdb",
        ssl_disabled=True
    )

# (ជំហានទី ១)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("🏠 ផ្ទះបុរី", callback_data="Borey")],
        [InlineKeyboardButton("🏢 Condo", callback_data="Condo")],
        [InlineKeyboardButton("🌍 ដីលក់", callback_data="Land")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "សួស្តី 👋\n"
        "សូមស្វាគមន៍មកកាន់ Real Estate Bot\n\n"
        "សូមជ្រើសរើសសេវាកម្ម:",
        reply_markup=reply_markup
    )
    return CHOOSING_TYPE

# (ជំហានទី ២)
async def handle_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['property_type'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("📍 ភ្នំពេញ", callback_data="Phnom_Penh")],
        [InlineKeyboardButton("📍 ខេត្តសៀមរាប", callback_data="Siem_Reap")],
        [InlineKeyboardButton("📍 ខេត្តបាត់ដំបង", callback_data="Battambang")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    selected_type = "ផ្ទះបុរី" if query.data == "Borey" else "Condo" if query.data == "Condo" else "ដីលក់"
    
    await query.edit_message_text(
        text=f"អ្នកបានជ្រើសរើស៖ {selected_type}\n\nតើលោកអ្នកចង់ស្វែងរកអចលនទ្រព្យនៅក្នុងតំបន់ណាដែរ?",
        reply_markup=reply_markup
    )
    return CHOOSING_LOCATION

# (ជំហានទី ៣)
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['location'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("ក្រោម $៥ ម៉ឺន", callback_data="under_50k")],
        [InlineKeyboardButton("$៥ ម៉ឺន - $១០ ម៉ឺន", callback_data="50k_100k")],
        [InlineKeyboardButton("$១០ ម៉ឺន - $២០ ម៉ឺន", callback_data="100k_200k")],
        [InlineKeyboardButton("លើសពី $២០ ម៉ឺន", callback_data="above_200k")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    loc_map = {"Phnom_Penh": "ភ្នំពេញ", "Siem_Reap": "ខេត្តសៀមរាប", "Battambang": "ខេត្តបាត់ដំបង"}
    selected_loc = loc_map.get(query.data, query.data)
    
    await query.edit_message_text(
        text=f"ទីតាំងដែលជ្រើសរើស៖ {selected_loc}\n\nតើកញ្ចប់ថវិកា (Budget) ដែលលោកអ្នកបានត្រៀមទុកមានចន្លោះប្រហែលប៉ុន្មានដែរ?",
        reply_markup=reply_markup
    )
    return CHOOSING_BUDGET

# (ជំហានទី ៤)
async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['budget'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("ទិញដាច់ (Cash)", callback_data="Cash")],
        [InlineKeyboardButton("បង់រំលស់ (Installment)", callback_data="Installment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="តើលោកអ្នកមានបំណងទិញដាច់ ឬចង់បង់រំលស់ដែរ?",
        reply_markup=reply_markup
    )
    return CHOOSING_PAYMENT

# (ជំហានទី ៥) សួររកឈ្មោះ
async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['payment_method'] = query.data
    
    await query.edit_message_text(text="សូមបញ្ចូលឈ្មោះរបស់អ្នក៖")
    return GETTING_NAME

# (ជំហានទី ៦) ទទួលឈ្មោះ រួចសួររកលេខទូរស័ព្ទ
async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text
    context.user_data['customer_name'] = user_name
    
    contact_keyboard = [
        [{"text": "📱 ចែករំលែកលេខទូរស័ព្ទ (Share Contact)", "request_contact": True}]
    ]
    reply_markup = ReplyKeyboardMarkup(contact_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "សូមបញ្ចូលលេខទូរស័ព្ទរបស់អ្នក (ឬចុចប៊ូតុងខាងក្រោមដើម្បីចែករំលែក)៖",
        reply_markup=reply_markup
    )
    return GETTING_PHONE

# (ជំហានទី ៧) ទទួលលេខទូរស័ព្ទ រួចធ្វើការវាយតម្លៃ & បញ្ចូល Database & ផ្ញើទៅ Agent
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = update.message.text
        
    first_name = context.user_data.get('customer_name')
    prop_type = context.user_data.get('property_type')
    location = context.user_data.get('location')
    budget = context.user_data.get('budget')
    payment = context.user_data.get('payment_method')
    
    # បម្លែងទិន្នន័យឲ្យត្រូវទម្រង់មុនបញ្ចូល Database និងផ្ញើទៅ Agent
    loc_map = {"Phnom_Penh": "Phnom Penh", "Siem_Reap": "Siem Reap", "Battambang": "Battambang"}
    budget_map = {"under_50k": "Under 50,000$", "50k_100k": "50,000$ - 100,000$", "100k_200k": "100,000$ - 200,000$", "above_200k": "Above 200,000$"}
    
    selected_loc = loc_map.get(location, location)
    display_budget = budget_map.get(budget, budget)
    khmer_loc = {"Phnom Penh": "ភ្នំពេញ", "Siem Reap": "ខេត្តសៀមរាប", "Battambang": "ខេត្តបាត់ដំបង"}.get(selected_loc, selected_loc)
    
    if budget == "under_50k":
        await update.message.reply_text(
            f"អរគុណលោក/អ្នកនាង {first_name} សម្រាប់ព័ត៌មាន!\n\n"
            "ជាការសោកស្ដាយ ពេលនេះគម្រោងដែលយើងមាន គឺមិនទាន់មានតម្លៃត្រូវនឹងកញ្ចប់ថវិការបស់លោកអ្នកនៅឡើយទេ។",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # ១. បញ្ចូលទិន្នន័យទៅកាន់ MySQL Database (Aiven)
        try:
            db = get_db_connection()
            cursor = db.cursor()
            
            # បង្កើតតារាងដោយស្វ័យប្រវត្តិ ប្រសិនបើវាមិនទាន់មានក្នុង Aiven (សំខាន់ណាស់!)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255) NOT NULL,
                phone_number VARCHAR(50) NOT NULL,
                property_type VARCHAR(100),
                location VARCHAR(100),
                budget VARCHAR(100),
                payment_method VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            sql = "INSERT INTO leads (customer_name, phone_number, property_type, location, budget, payment_method) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (first_name, phone_number, prop_type, selected_loc, display_budget, payment)
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            print("✅ Data saved to Aiven Database successfully!")
        except Exception as e:
            print(f"❌ Database Error: {e}")

        # ២. ទម្រង់សារដែលត្រូវផ្ញើទៅ Agent
        agent_message = (
            "📢 New Lead\n\n"
            f"👤 Name: {first_name}\n"
            f"📞 Phone: {phone_number}\n"
            f"🏠 Property: {prop_type}\n"
            f"💰 Budget: {display_budget}\n"
            f"📍 Location: {selected_loc}"
        )
        
        # ៣. ផ្ញើសារទៅកាន់ Agent (ឬ Group)
        try:
            await context.bot.send_message(chat_id=AGENT_CHAT_ID, text=agent_message)
            print("✅ Message sent to Agent!")
        except Exception as e:
            print(f"❌ Telegram Send Error: {e}")

        # ៤. ផ្ញើសារបញ្ជាក់ទៅកាន់អតិថិជន
        await update.message.reply_text(
            f"អរគុណលោក/អ្នកនាង {first_name} សម្រាប់ការផ្ដល់ព័ត៌មាន!\n\n"
            f"ព័ត៌មានរបស់លោកអ្នកត្រូវបានបញ្ចូលទៅក្នុងប្រព័ន្ធហើយ។ ភ្នាក់ងារជំនាញប្រចាំ {khmer_loc} នឹងទាក់ទងទៅកាន់លេខទូរស័ព្ទ {phone_number} ក្នុងពេលឆាប់ៗនេះ។",
            reply_markup=ReplyKeyboardRemove()
        )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "ការសាកសួរត្រូវបានបោះបង់។ ប្រសិនបើលោកអ្នកចង់ចាប់ផ្ដើមឡើងវិញ សូមវាយពាក្យ /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    
    # កំណត់ ConversationHandler ឱ្យបានត្រឹមត្រូវ
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
    
    app.add_handler(conv_handler)
    
    print("Starting Webhook...")
    
    # ប្រើ run_webhook តែមួយគត់
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()