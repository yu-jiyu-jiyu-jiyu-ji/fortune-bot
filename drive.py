from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os
import json
import base64
from google.oauth2.service_account import Credentials

# ===============================
# Google Drive 認証
# ===============================
if os.getenv("GOOGLE_CREDENTIALS_B64"):
    service_account_info = json.loads(
        base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_B64")).decode("utf-8")
    )
else:
    raise ValueError("環境変数 GOOGLE_CREDENTIALS_B64 が設定されていません")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# 保存先フォルダ ID を環境変数で管理
FOLDER_ID = os.getenv("1oFhe_9yzsrPSD-aqnKcRcvWKvfUkFcRS")

def upload_file_to_drive(file_storage, filename):
    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID] if FOLDER_ID else []
    }
    media = MediaIoBaseUpload(
        io.BytesIO(file_storage.read()),  # Flask FileStorage → BytesIO
        mimetype=file_storage.mimetype,
        resumable=True
    )
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()
    return file.get("webViewLink")
