from flask import request, redirect
from sheets import append_user_data
from drive import save_images_to_drive
import logging

def handle_form_submission():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    birthday = request.form.get("birthday")
    left_hand = request.files.get("left_hand")
    right_hand = request.files.get("right_hand")

    try:
        logging.info(f"[フォーム受信] user_id={user_id}, name={name}, birthday={birthday}")
        # 画像保存
        save_images_to_drive(user_id, {
            "Lhand.png": left_hand,
            "Rhand.png": right_hand
        })
        # スプレッドシート保存
        append_user_data(user_id, name, birthday)
        logging.info("[登録成功] スプレッドシートと画像保存が完了")
    except Exception as e:
        logging.exception(f"[登録失敗] 処理中にエラー発生: {e}")

    return redirect("/thanks")
