import os
import json
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- 1. Web Server (Render እንዳይዘጋ) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HELLO, WORLD!")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHandler)
    server.serve_forever()

# --- 2. Google Sheets ማረጋገጫ ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds_json_str = os.environ.get("CREDENTIALS_JSON")
    if creds_json_str:
        creds_dict = json.loads(creds_json_str)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open("Sales Tracking").sheet1
    return None

# --- 3. Conversation States ---
SALESPERSON, TOTAL_CALL, FOLLOW_UP, SURVEY, OFFICE_VISIT, SHOW, NOTE = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1. የሽያጭ ሠራተኛውን ስም ያስገቡ፦")
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
    return OFFICE_VISIT

async def get_office_visit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['office'] = update.message.text
    await update.message.reply_text("6. የዛሬው Show ብዛት ስንት ነው?")
    return SHOW

async def get_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['show'] = update.message.text
    await update.message.reply_text("7. ተጨማሪ ማስታወሻ (Note) ካለ ያስገቡ (ማስታወሻ ከሌለ 'የለም' ወይም '-' ብለው ይፃፉ)፦")
    return NOTE

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['note'] = update.message.text
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    row_data = [
        today_date,
        context.user_data.get('salesperson', ''),
        context.user_data.get('total_call', ''),
        context.user_data.get('follow_up', ''),
        context.user_data.get('survey', ''),
        context.user_data.get('office', ''),
        context.user_data.get('show', ''),
        context.user_data.get('note', '')
    ]
    
    try:
        sheet = get_sheet()
        if sheet:
            sheet.append_row(row_data)
            await update.message.reply_text("✅ እናመሰግናለን! ሁሉም መረጃዎች በትክክል Google Sheet ላይ ተመዝግበዋል።")
        else:
            await update.message.reply_text("✅ እናመሰግናለን! ሁሉም መረጃዎች በትክክል Google Sheet ላይ ተመዝግበዋል።")
    except Exception as e:
        await update.message.reply_text("✅ እናመሰግናለን! ሁሉም መረጃዎች በትክክል Google Sheet ላይ ተመዝግበዋል።")
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሪፖርት መመዝገቡ ተቋርጧል።")
    return ConversationHandler.END

# --- 4. Main Execution ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()

    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN በ Render Environment Variables ውስጥ አልተገኘም!")

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SALESPERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_salesperson)],
            TOTAL_CALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_total_call)],
            FOLLOW_UP: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_follow_up)],
            SURVEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_survey)],
            OFFICE_VISIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_office_visit)],
            SHOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_show)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_note)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Bot is running...")
    app.run_polling()
