import base64, os, json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io
import logging

# Google Drive API サービスの取得
def get_drive_service():
    encoded = os.environ.get("GOOGLE_CREDENTIALS_B64")
    if not encoded:
        raise RuntimeError("GOOGLE_CREDENTIALS_B64 not set.")

    credentials_dict = json.loads(base64.b64decode(encoded).decode())
    creds = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    return build('drive', 'v3', credentials=creds)

# フォルダ内に画像をアップロード（user_idごとにファイル名固定）
def save_images_to_drive(user_id, image_dict):
    drive_service = get_drive_service()
    folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not folder_id:
        raise RuntimeError("DRIVE_FOLDER_ID not set.")

    for filename, file_storage in image_dict.items():
        if file_storage:
            file_metadata = {
                'name': f"{user_id}_{filename}",
                'parents': [folder_id]
            }
            media = MediaIoBaseUpload(
                io.BytesIO(file_storage.read()),
                mimetype=file_storage.mimetype,
                resumable=True
            )
            try:
                drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logging.info(f"Uploaded {filename} for user {user_id}")
            except Exception as e:
                logging.error(f"Upload failed for {filename}: {str(e)}")
