import os
import gspread
from google.oauth2.service_account import Credentials
import json
import base64
from datetime import datetime, date

# ===============================
# Google Sheets 認証
# ===============================
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Render 環境変数から service account 情報を取得
if os.getenv("GOOGLE_CREDENTIALS_B64"):
    service_account_info = json.loads(
        base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_B64")).decode("utf-8")
    )
else:
    raise ValueError("環境変数 GOOGLE_CREDENTIALS_B64 が設定されていません")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1


# ===============================
# 日付正規化関数
# ===============================
def normalize_date(value):
    """スプレッドシートから取得した日付を正規化"""
    if not value or value in ("", "1899/12/30"):  # 空 or デフォルト値
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y/%m/%d").date()
    except Exception:
        return None


# ===============================
# ユーザー情報の取得
# ===============================
def get_user_profile(user_id):
    records = sheet.get_all_records()
    for row in records:
        if row["user_id"] == user_id:
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "birthday": row["birthday"],
                "face_image": row.get("face_image", ""),
                "right_hand": row.get("right_hand", ""),
                "left_hand": row.get("left_hand", ""),
                "limit": int(row.get("limit", 1) or 1),
                "last_fortune_date": normalize_date(row.get("last_fortune_date")),
                "count_today": int(row.get("count_today", 0) or 0),
            }
    return None


# ===============================
# ユーザー情報の更新
# ===============================
def update_user_fortune(user_id, last_fortune_date, count_today):
    records = sheet.get_all_records()
    for i, row in enumerate(records, start=2):  # header行を除外するので+2
        if row["user_id"] == user_id:
            sheet.update_cell(i, 8, last_fortune_date.strftime("%Y/%m/%d"))
            sheet.update_cell(i, 9, count_today)
            return True
    return False
