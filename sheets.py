import os
import json
import base64
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# -----------------------------
# Google Sheets 接続設定
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# 環境変数から認証情報を読み込み（Base64 → JSON）
b64_credentials = os.getenv("GOOGLE_CREDENTIALS_B64")
if not b64_credentials:
    raise RuntimeError("環境変数 GOOGLE_CREDENTIALS_B64 が設定されていません")

service_account_info = json.loads(base64.b64decode(b64_credentials).decode("utf-8"))
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# gspread クライアントを作成
client = gspread.authorize(creds)

# スプレッドシートを取得
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1


# -----------------------------
# ユーザー情報登録
# -----------------------------
def append_user_data(user_id, name, birthday, face_image="", right_hand="", left_hand="", limit=1):
    try:
        today_str = datetime.now().strftime("%Y/%m/%d")
        sheet.append_row([
            user_id,
            name,
            birthday,
            face_image,
            right_hand,
            left_hand,
            limit,
            "",   # last_fortune_date（空で開始）
            0    # count_today
        ])
        print(f"✅ ユーザー登録完了: {user_id}")
    except Exception as e:
        print(f"❌ ユーザー登録エラー: {e}")


# -----------------------------
# ユーザー情報取得
# -----------------------------
def get_user_profile(user_id):
    try:
        records = sheet.get_all_records()
        for row in records:
            if row["user_id"] == user_id:
                name = row.get("name", "")
                birthday = row.get("birthday", "")
                print(f"🧾 プロフィール取得: ({name}, {birthday})")
                return {"name": name, "birthday": birthday}
    except Exception as e:
        print(f"❌ プロフィール取得エラー: {e}")
    return None


# -----------------------------
# 本日の占いが可能かチェック
# -----------------------------
def can_ask_fortune_today(user_id):
    try:
        cell = sheet.find(user_id)
        if not cell:
            return False

        row = cell.row
        last_date = sheet.cell(row, 8).value  # last_fortune_date
        count_today = sheet.cell(row, 9).value  # count_today
        limit = sheet.cell(row, 7).value       # limit

        today_str = datetime.now().strftime("%Y/%m/%d")

        # 初回 or 日付が変わったらリセット
        if last_date != today_str:
            sheet.update_cell(row, 8, today_str)  # 更新日
            sheet.update_cell(row, 9, 0)          # count_today = 0
            count_today = 0

        if count_today == "":
            count_today = 0
        else:
            count_today = int(count_today)

        if limit == "":
            limit = 1
        else:
            limit = int(limit)

        return count_today < limit

    except Exception as e:
        print(f"❌ リクエスト確認エラー: {e}")
        return False


# -----------------------------
# リクエスト回数をカウントアップ
# -----------------------------
def increment_fortune_count(user_id):
    try:
        cell = sheet.find(user_id)
        if not cell:
            return
        row = cell.row
        count_today = sheet.cell(row, 9).value
        if count_today == "":
            count_today = 0
        else:
            count_today = int(count_today)
        sheet.update_cell(row, 9, count_today + 1)
        print("✅ カウント更新完了")
    except Exception as e:
        print(f"❌ カウント更新エラー: {e}")
