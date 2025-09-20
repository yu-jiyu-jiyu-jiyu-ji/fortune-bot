import base64
import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証情報を取得してgspreadクライアント生成
def get_credentials():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    encoded = os.environ.get("GOOGLE_CREDENTIALS_B64")
    if not encoded:
        raise RuntimeError("GOOGLE_CREDENTIALS_B64 not set.")
    credentials_dict = json.loads(base64.b64decode(encoded).decode())
    return ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

# スプレッドシートとワークシートを取得
def get_sheet():
    gc = gspread.authorize(get_credentials())
    sheet_id = os.environ["SPREADSHEET_ID"]
    worksheet = gc.open_by_key(sheet_id).sheet1
    return worksheet

# 初回登録時のデータ追加処理（画像は任意）
def append_user_data(user_id, name, birthday, face_image="", right_hand="", left_hand=""):
    try:
        sheet = get_sheet()
        limit = 1  # デフォルトの上限
        last_fortune_date = ""  # 初期は空
        count_today = 0
        sheet.append_row([
            user_id, name, birthday,
            face_image or "", right_hand or "", left_hand or "",
            limit, last_fortune_date, count_today
        ])
        print("✅ スプレッドシートに書き込み完了")
    except Exception as e:
        print(f"❌ スプレッドシート書き込み失敗: {e}")

# ユーザーの1日あたりリクエスト可能かをチェック
def can_ask_fortune_today(user_id):
    try:
        sheet = get_sheet()
        records = sheet.get_all_records()
        today = datetime.now().strftime("%Y/%m/%d")
        for i, row in enumerate(records):
            if row["user_id"] == user_id:
                count_today = int(row.get("count_today", 0))
                last_date = row.get("last_fortune_date", "")
                limit = int(row.get("limit", 1))
                if last_date != today:
                    return True  # 日付が変わった＝リセットOK
                else:
                    return count_today < limit
        return False
    except Exception as e:
        print(f"❌ リクエスト確認エラー: {e}")
        return False

# 今日のリクエスト数をインクリメント or 日付更新
def increment_fortune_count(user_id):
    try:
        sheet = get_sheet()
        today = datetime.now().strftime("%Y/%m/%d")
        cell = sheet.find(user_id)
        row_num = cell.row
        last_date = sheet.cell(row_num, 9).value  # last_fortune_date列
        count_today = int(sheet.cell(row_num, 10).value or 0)

        if last_date != today:
            sheet.update_cell(row_num, 9, today)
            sheet.update_cell(row_num, 10, 1)
        else:
            sheet.update_cell(row_num, 10, count_today + 1)
        print("✅ カウント更新完了")
    except Exception as e:
        print(f"❌ カウント更新失敗: {e}")

# 名前と誕生日を取得（占い用）
def get_user_profile(user_id):
    sheet = SHEET
    records = sheet.get_all_records()

    for row in records:
        if row["user_id"] == user_id:
            try:
                return {
                    "name": row["name"],
                    "birthday": row["birthday"],
                    "face_image": row.get("face_image", ""),
                    "right_hand": row.get("right_hand", ""),
                    "left_hand": row.get("left_hand", ""),
                    "limit": int(row["limit"]) if str(row["limit"]).isdigit() else 1,
                    "last_fortune_date": row.get("last_fortune_date", ""),
                    "count_today": int(row["count_today"]) if str(row["count_today"]).isdigit() else 0
                }
            except Exception as e:
                print(f"❌ プロフィール変換エラー: {e}, row={row}")
                return None
    return None

