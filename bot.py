import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. የ Google Sheets ማረጋገጫ (Credentials) ---
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
        
        # ማሳሰቢያ፡ "Sales_Report" የሚለውን አንተ በከፈትከው ትክክለኛው የ Google Sheet ስም ቀይረው
        return client.open("Sales Tracking").sheet1 
    return None

# --- 2. ቦቱ ሲጀመር የሚሰጠው ምላሽ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! የ NEXORA Business Group የሽያጭ እና ክትትል ሪፖርት መቀበያ ቦት ነው። ዕለታዊ ሪፖርትህን አሁን መላክ ትችላለህ።")

# --- 3. ሪፖርት ሲላክ ወደ Sheet የሚያስገባው ክፍል ---
async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.message.from_user.first_name
    report_text = update.message.text
    
    try:
        sheet = get_sheet()
        if sheet:
            # ስሙን እና የላከውን ሪፖርት በ Sheet ላይ ማስገባት
            sheet.append_row([user_name, report_text])
            await update.message.reply_text("ሪፖርትህ በስኬት ተመዝግቧል! እናመሰግናለን።")
        else:
            await update.message.reply_text("የ Google Sheets ማረጋገጫ (CREDENTIALS_JSON) አልተገኘም።")
    except Exception as e:
        await update.message.reply_text("ይቅርታ፣ ስህተት ተፈጥሯል (የ Sheet ስም ትክክል መሆኑን አረጋግጥ)።")

# --- 4. ቦቱ ሳይዘጋ 24 ሰዓት እንዲሰራ የሚያደርገው (Main Loop) ---
if name == 'main':
    # ከ Render Environment Variables ውስጥ የቴሌግራም ቶከኑን ይወስዳል
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report))
    
    print("Bot is running successfully...")
    app.run_polling()
