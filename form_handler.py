# form_handler.py
from flask import Blueprint, request, render_template_string
from sheets import append_user_data

form_bp = Blueprint("form", __name__)

# HTMLフォーム
FORM_HTML = """
<!doctype html>
<html>
  <head><title>プロフィール登録フォーム</title></head>
  <body>
    <h2>プロフィール登録</h2>
    <form method="post">
      <label>氏名（変更不可）:</label><br>
      <input type="text" name="name" required><br><br>
      
      <label>生年月日（変更不可 / YYYY-MM-DD）:</label><br>
      <input type="date" name="birthday" required><br><br>
      
      <label>顔写真 (任意URL):</label><br>
      <input type="text" name="face_image"><br><br>
      
      <label>右手の写真 (任意URL):</label><br>
      <input type="text" name="right_hand"><br><br>
      
      <label>左手の写真 (任意URL):</label><br>
      <input type="text" name="left_hand"><br><br>
      
      <input type="hidden" name="user_id" value="{{ user_id }}">
      <button type="submit">登録</button>
    </form>
  </body>
</html>
"""

# フォーム表示
@form_bp.route("/form", methods=["GET"])
def show_form():
    user_id = request.args.get("user_id", "")
    return render_template_string(FORM_HTML, user_id=user_id)

# フォーム送信
@form_bp.route("/form", methods=["POST"])
def submit_form():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    birthday = request.form.get("birthday")
    face_image = request.form.get("face_image", "")
    right_hand = request.form.get("right_hand", "")
    left_hand = request.form.get("left_hand", "")

    append_user_data(user_id, name, birthday, face_image, right_hand, left_hand)

    return "登録が完了しました。LINEに戻って『今日の運勢』と送ってください。"
