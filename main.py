from flask import Flask, request, render_template, abort
from linebot.exceptions import InvalidSignatureError

# LINE用 handler をインポート
from line_handler import handler  

from form_handler import form_bp, handle_form_submission  # ← 修正


app = Flask(__name__)
app.register_blueprint(form_bp)  # Blueprint 登録


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

# 登録完了ページ
@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

# ユーザー登録フォームの表示
@app.route("/register")
def register():
    uid = request.args.get("user_id", "")
    return render_template("register.html", user_id=uid)

# フォーム送信処理
@app.route("/submit", methods=["POST"])
def submit():
    return handle_form_submission()

# ヘルスチェック用
@app.route("/")
def index():
    return "Hello! LINE Fortune Bot is running."

# ローカル実行用
if __name__ == "__main__":
    app.run(debug=True)
