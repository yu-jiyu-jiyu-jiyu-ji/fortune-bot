import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 環境変数からサービスアカウント情報を取得
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)

# gspread クライアントを作成
client = gspread.authorize(creds)

# 📌 スプレッドシートIDは環境変数で管理
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1


def get_user_row(user_id):
    """ユーザーIDに対応する行番号を返す（見つからなければNone）"""
    values = sheet.get_all_values()
    for idx, row in enumerate(values[1:], start=2):  # 1行目はヘッダーなので2行目から
        if row[0] == user_id:
            return idx
    return None


def get_user_data(user_id):
    """ユーザーのデータを取得"""
    row = get_user_row(user_id)
    if row:
        data = sheet.row_values(row)
        # ヘッダーと突き合わせて辞書形式に変換
        headers = sheet.row_values(1)
        return dict(zip(headers, data))
    return None


def create_user(user_id, name="", birthday="", face_image="", right_hand="", left_hand="", limit=1):
    """新規ユーザーを追加"""
    sheet.append_row([
        user_id, name, birthday, face_image, right_hand, left_hand,
        str(limit), "", "0"
    ])


def update_user(user_id, updates: dict):
    """ユーザー情報を更新（updatesは {カラム名: 値} の辞書）"""
    headers = sheet.row_values(1)
    row = get_user_row(user_id)
    if not row:
        return False

    for key, value in updates.items():
        if key in headers:
            col = headers.index(key) + 1
            sheet.update_cell(row, col, value)
    return True


def can_receive_fortune(user_id):
    """本日の占い利用可否を確認し、利用回数を更新"""
    user = get_user_data(user_id)
    if not user:
        return False, "ユーザーが登録されていません。"

    today = datetime.now().strftime("%Y-%m-%d")  # ✅ 日付は YYYY-MM-DD に統一
    last_date = user.get("last_fortune_date", "")
    count_today = int(user.get("count_today", "0") or 0)
    limit = int(user.get("limit", "1") or 1)

    if last_date != today:
        # 新しい日 → カウントをリセット
        update_user(user_id, {
            "last_fortune_date": today,
            "count_today": "1"
        })
        return True, "初回利用"

    if count_today < limit:
        # 制限内 → カウントを加算
        update_user(user_id, {
            "count_today": str(count_today + 1)
        })
        return True, "回数内利用"

    return False, "本日の利用回数上限です"
