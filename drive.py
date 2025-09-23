import io
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials
import json
import base64

# 認証情報の読み込み
if os.getenv("GOOGLE_CREDENTIALS_B64"):
    service_account_info = json.loads(
        base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_B64")).decode("utf-8")
    )
else:
    raise ValueError("環境変数 GOOGLE_CREDENTIALS_B64 が設定されていません")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# ファイルアップロード関数
def upload_file_to_drive(file_storage, filename):
    file_metadata = {"name": filename}
    media = MediaIoBaseUpload(file_storage.stream, mimetype=file_storage.mimetype)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded_file.get("id")

    # 公開リンクを有効化
    drive_service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"},
    ).execute()

    return f"https://drive.google.com/uc?id={file_id}"
