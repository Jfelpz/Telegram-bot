import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==========================
# AUTHENTICADOR
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

client = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(GOOGLE_CREDENTIALS),
        scope
    )
)

spreadsheet = client.open_by_key(SHEET_ID)

sheet = spreadsheet.worksheet("MENU")
config_sheet = spreadsheet.worksheet("CONFIG")
