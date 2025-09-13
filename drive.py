from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

# 認証（初回はブラウザ認証が必要）
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")

if gauth.credentials is None:
    # 認証情報がなければブラウザ認証
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # トークンが切れていたらリフレッシュ
    gauth.Refresh()
else:
    # 既存の認証情報を使う
    gauth.Authorize()

# 認証情報を保存
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

# 指定フォルダ内に、user_id名のフォルダを作成（なければ）
def get_or_create_user_folder(parent_folder_id, user_id):
    query = f"'{parent_folder_id}' in parents and title = '{user_id}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        return file_list[0]['id']  # 既存フォルダIDを返す
    else:
        folder_metadata = {
            'title': user_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_folder_id}]
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        return folder['id']

# ファイルをアップロードして Drive 内に保存
def upload_file_to_drive(folder_id, file_storage, filename):
    file_drive = drive.CreateFile({
        'title': filename,
        'parents': [{'id': folder_id}]
    })
    file_drive.SetContentFile(file_storage)
    file_drive.Upload()
