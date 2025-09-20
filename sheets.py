import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os

# Google認証
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "service_account.json"

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
client = gspread.authorize(creds)

# 環境変数からスプレッドシートID取得
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET = client.open_by_key(SPREADSHEET_ID).sheet1


def get_user_profile(user_id):
    """ユーザー情報を取得"""
    records = SHEET.get_all_records()

    for row in records:
        if row["user_id"] == user_id:
            try:
                # limit
                limit_val = row.get("limit", 1)
                limit = int(limit_val) if str(limit_val).isdigit() else 1

                # count_today
                count_val = row.get("count_today", 0)
                count_today = int(count_val) if str(count_val).isdigit() else 0

                # last_fortune_date を安全に文字列化
                last_date = row.get("last_fortune_date", "")
                if isinstance(last_date, (int, float)):
                    base_date = datetime(1899, 12, 30)  # Google Sheets起点
                    last_date = (base_date + timedelta(days=int(last_date))).strftime("%Y/%m/%d")
                elif isinstance(last_date, datetime):
                    last_date = last_date.strftime("%Y/%m/%d")
                else:
                    last_date = str(last_date).strip()

                return {
                    "name": row.get("name", ""),
                    "birthday": row.get("birthday", ""),
                    "face_image": row.get("face_image", ""),
                    "right_hand": row.get("right_hand", ""),
                    "left_hand": row.get("left_hand", ""),
                    "limit": limit,
                    "last_fortune_date": last_date,  # ←常に "YYYY/MM/DD" 文字列
                    "count_today": count_today
                }
            except Exception as e:
                print(f"❌ プロフィール変換エラー: {e}, row={row}")
                return None
    return None


def can_ask_fortune_today(user_id):
    """今日占えるか確認"""
    profile = get_user_profile(user_id)
    if not profile:
        return False

    today = datetime.now().strftime("%Y/%m/%d")
    last_date = profile.get("last_fortune_date", "")
    count_today = profile.get("count_today", 0)
    limit = profile.get("limit", 1)

    # 日付リセット判定
    if last_date != today:
        reset_fortune_count(user_id)

    return count_today < limit


def increment_fortune_count(user_id):
    """占い利用カウントをインクリメント"""
    try:
        records = SHEET.get_all_records()
        for i, row in enumerate(records, start=2):  # 2行目から
            if row["user_id"] == user_id:
                today = datetime.now().strftime("%Y/%m/%d")

                # 現在のカウント
                count_val = row.get("count_today", 0)
                count_today = int(count_val) if str(count_val).isdigit() else 0

                SHEET.update_cell(i, 8, today)           # last_fortune_date
                SHEET.update_cell(i, 9, count_today + 1) # count_today
                print("✅ カウント更新完了")
                return True
    except Exception as e:
        print(f"❌ カウント更新エラー: {e}")
    return False


def reset_fortune_count(user_id):
    """新しい日になったら count_today をリセット"""
    try:
        records = SHEET.get_all_records()
        for i, row in enumerate(records, start=2):
            if row["user_id"] == user_id:
                today = datetime.now().strftime("%Y/%m/%d")
                SHEET.update_cell(i, 8, today)  # last_fortune_date
                SHEET.update_cell(i, 9, 0)      # count_today
                print("✅ カウントリセット完了")
                return True
    except Exception as e:
        print(f"❌ カウントリセットエラー: {e}")
    return False
