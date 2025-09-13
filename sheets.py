import base64, os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_credentials():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    encoded = os.environ.get("GOOGLE_CREDENTIALS_B64")
    if not encoded:
        raise RuntimeError("GOOGLE_CREDENTIALS_B64 not set.")
    credentials_dict = json.loads(base64.b64decode(encoded).decode())
    return ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

def append_user_data(user_id, name, birthday):
    try:
        gc = gspread.authorize(get_credentials())
        sheet_id = os.environ["SPREADSHEET_ID"]
        sheet = gc.open_by_key(sheet_id).sheet1

        # 行として追加
        sheet.append_row([user_id, name, birthday])

        print("✅ スプレッドシートに書き込み完了")

    except Exception as e:
        print(f"❌ スプレッドシート書き込み失敗: {e}")
