import os
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Render Port እንዳይዘጋ Dummy Web Server ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

# --- 2. የ Google Sheets ማረጋገጫ ---
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
        return client.open("Sales Tracking").sheet1  # የ Sheet ስምህን እዚህ ጋር አስተካክለው
    return None

# --- 3. የቦት ምላሾች ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ NEXORA Business Group የሽያጭ እና ክትትል ሪፖርት መቀበያ ቦት ነው። ዕለታዊ ሪፖርትህን አሁን መላክ ትችላለህ።")

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    report_text = update.message.text
    
    try:
        sheet = get_sheet()
        if sheet:
            sheet.append_row([user_name, report_text])
            await update.message.reply_text("ሪፖርትህ በስኬት ተመዝግቧል! እናመሰግናለን።")
        else:
            await update.message.reply_text("የ Google Sheets ማረጋገጫ አልተገኘም።")
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ ስህተት ተፈጥሯል።")

#  --- 4. Main Execution ---
if __name__ == '__main__':
    threading.Thread(target=run_web_server, daemon=True).start()
    
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN በ Render Environment Variables ውስጥ አልተገኘም!")
        
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report))
    
    print("Bot is running...")
    app.run_polling()
