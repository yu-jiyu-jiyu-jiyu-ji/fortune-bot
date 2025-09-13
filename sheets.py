import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

# Google Sheets 認証設定
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# credentials.json のパス（ファイル名が異なる場合は変更）
CREDS_FILE = "fortunebot-472012-ac0967c639f9.json"
SPREADSHEET_KEY = os.getenv("SPREADSHEET_KEY")  # .envや環境変数で設定しておくと◎

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_KEY).sheet1  # 最初のシートを開く

# ユーザー情報を追記する関数
def append_user_data(user_id, name, birthday):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, user_id, name, birthday]
    sheet.append_row(row)
