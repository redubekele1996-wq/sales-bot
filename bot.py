import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scopes
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Read credentials from Render Environment Variable
creds_json_str = os.environ.get("CREDENTIALS_JSON")

if creds_json_str:
    creds_dict = json.loads(creds_json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    # Fallback to file if running locally
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

client = gspread.authorize(creds)
