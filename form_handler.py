from flask import Blueprint, request, render_template
from sheets import append_user_data
from drive import upload_file_to_drive

form_bp = Blueprint("form", __name__)

# フォーム表示
@form_bp.route("/form", methods=["GET"])
def show_form():
    user_id = request.args.get("user_id", "")
    return render_template("register.html", user_id=user_id)

# フォーム送信処理
@form_bp.route("/submit", methods=["POST"])
def handle_form_submission():
    try:
        user_id = request.form.get("user_id", "")
        name = request.form.get("name", "")
        birthday = request.form.get("birthday", "")
        face_image = request.form.get("face_image", "")
        right_hand = request.form.get("right_hand", "")
        left_hand = request.form.get("left_hand", "")
        limit = int(request.form.get("limit", 1))

        # アップロードファイルを Drive に保存（存在する場合のみ）
        face_image_url = ""
        right_hand_url = ""
        left_hand_url = ""

        if "face_image" in request.files and request.files["face_image"].filename:
            face_image_url = upload_file_to_drive(request.files["face_image"], f"{user_id}_face")

        if "right_hand" in request.files and request.files["right_hand"].filename:
            right_hand_url = upload_file_to_drive(request.files["right_hand"], f"{user_id}_right")

        if "left_hand" in request.files and request.files["left_hand"].filename:
            left_hand_url = upload_file_to_drive(request.files["left_hand"], f"{user_id}_left")

        # スプレッドシートに保存
        append_user_data(user_id, name, birthday, face_image_url, right_hand_url, left_hand_url, limit=1)

        return render_template("thanks.html")

    except Exception as e:
        import traceback
        return f"エラー: {e}<br><pre>{traceback.format_exc()}</pre>", 500
    