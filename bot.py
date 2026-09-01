import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Sales Tracking").sheet1

# Conversation States
SALESPERSON, TOTAL_CALL, FOLLOW_UP, SURVEY, OFFICE, WALK_IN, NOTE = range(7)

# Telegram Bot Token
BOT_TOKEN = "8584994166:AAGn2jYyVYHr6CdT5P4VyuMbgAitYrmookM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የዕለታዊ Sales ሪፖርት መመዝገቢያ ነው።\n\n1. የስምዎትን አካውንት/የሽያጭ ሰራተኛውን ስም ያስገቡ፦")
    return SALESPERSON

async def get_salesperson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['salesperson'] = update.message.text
    await update.message.reply_text("2. የዛሬው Total Call ብዛት ስንት ነው?")
    return TOTAL_CALL

async def get_total_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['total_call'] = update.message.text
    await update.message.reply_text("3. የዛሬው Follow-up ብዛት ስንት ነው?")
    return FOLLOW_UP

async def get_follow_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['follow_up'] = update.message.text
    await update.message.reply_text("4. የዛሬው Survey ብዛት ስንት ነው?")
    return SURVEY

async def get_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['survey'] = update.message.text
    await update.message.reply_text("5. የዛሬው Office Visit ብዛት ስንት ነው?")
    return OFFICE

async def get_office(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['office'] = update.message.text
    await update.message.reply_text("6. የዛሬው Walk-in ብዛት ስንት ነው?")
    return WALK_IN

async def get_walk_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['walk_in'] = update.message.text
    await update.message.reply_text("7. ተጨማሪ ማስታወሻ (Note) ካለ ያስገቡ (ማስታወሻ ከሌለ 'የለም' ወይም '-' ብለው ይጻፉ)፦")
    return NOTE

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['note'] = update.message.text
    
    # የዛሬውን ቀን በ YYYY-MM-DD ቅርጸት መውሰድ
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # ወደ Google Sheet የሚገባው መረጃ በቅደም ተከተል
    row_data = [
        today_date,
        context.user_data['salesperson'],
        context.user_data['total_call'],
        context.user_data['follow_up'],
        context.user_data['survey'],
        context.user_data['office'],
        context.user_data['walk_in'],
        context.user_data['note']
    ]
    
    try:
        sheet.append_row(row_data)
        await update.message.reply_text("✅ እናመሰግናለን! ሁሉም መረጃዎች በትክክል Google Sheet ላይ ተመዝግበዋል።")
    except Exception as e:
        await update.message.reply_text(f"❌ ስህተት ተፈጥሯል: {str(e)}")
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ምዝገባው ተቋርጧል። እንደገና ለመጀመር /start ብለው ይጻፉ።")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SALESPERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_salesperson)],
            TOTAL_CALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_total_call)],
            FOLLOW_UP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_follow_up)],
            SURVEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_survey)],
            OFFICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_office)],
            WALK_IN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_walk_in)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_note)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()
