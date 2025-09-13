from flask import request, redirect
from sheets import append_user_data
from drive import save_images_to_drive

# `/submit` の POST 処理
def handle_form_submission():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    birthday = request.form.get("birthday")
    left_hand = request.files.get("left_hand")
    right_hand = request.files.get("right_hand")

    # Google Drive に画像保存（userId フォルダに上書き保存）
    save_images_to_drive(user_id, {
        "Lhand.png": left_hand,
        "Rhand.png": right_hand
    })

    # スプレッドシートにユーザ情報を保存
    append_user_data(user_id, name, birthday)

    return redirect("/thanks")
