from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# LINE APIトークン（環境変数から取得）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 🔗 ルート：LINEのWebhook受け取り用
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# 🤖 メッセージイベント処理（テキスト受信時）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text

    # 仮の処理：挨拶に反応してリンク送信
    if message_text in ["こんにちは", "はじめまして"]:
        register_url = f"https://fortune-bot-p2ey.onrender.com/register?uid={user_id}"
        reply = f"{user_id}さん、初めまして！\nまずはこちらから登録をお願いします👇\n{register_url}"
    else:
        reply = "メッセージを受け取りました！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

# 📝 新規ユーザー登録ページ表示
@app.route("/register")
def register():
    uid = request.args.get("uid", "")
    return render_template("register.html", uid=uid)

# ✅ ヘルスチェック用（オプション）
@app.route("/")
def index():
    return "Hello! LINE Fortune Bot is running."

# if __name__ == "__main__":
#     app.run()
