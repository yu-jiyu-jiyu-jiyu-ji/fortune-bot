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

# スプレッドシートへ接続
gc = gspread.authorize(get_credentials())
sheet_id = os.environ["SPREADSHEET_ID"]
sheet = gc.open_by_key(sheet_id).User

# 🔽 これを追加！
def append_user_data(user_data: dict):
    """
    ユーザーデータ（辞書）をスプレッドシートに追記する
    """
    # ヘッダー行の順に並べる
    headers = sheet.row_values(1)
    row = [user_data.get(key, "") for key in headers]
    sheet.append_row(row)
