from flask import Flask, request, render_template, abort
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from line_handler import handler
from form_handler import submit_user_info

app = Flask(__name__)

# LINE Webhook受信エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    from line_handler import line_bot_api  # 遅延インポートで循環参照防止
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# ユーザー登録フォームの表示
@app.route("/register")
def register():
    uid = request.args.get("uid", "")
    return render_template("register.html", user_id=uid)

# フォーム送信処理
@app.route("/submit", methods=["POST"])
def submit():
    return submit_user_info(request)

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

# ヘルスチェック用ルート
@app.route("/")
def index():
    return "Hello! LINE Fortune Bot is running."

# 実行用
if __name__ == "__main__":
    app.run(debug=True)
