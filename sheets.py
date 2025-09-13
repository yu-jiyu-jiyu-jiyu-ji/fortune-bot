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

# 取得して使用
gc = gspread.authorize(get_credentials())
sheet = gc.open_by_key("SPREADSHEET_ID").sheet1
