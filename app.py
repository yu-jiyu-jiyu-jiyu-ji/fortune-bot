from flask import Flask, request, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

app = Flask(__name__)

# LINEチャンネル設定（Renderの環境変数に設定しておく）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

# 登録済ユーザーを簡易的に保存（PoCでは辞書。実運用はDB or スプシ）
user_profiles = {}  # user_id → {name, birthday, image_url}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip()

    # 初回登録フロー
    if user_id not in user_profiles:
        profile = line_bot_api.get_profile(user_id)
        register_url = f"https://your-render-app.onrender.com/register?uid={user_id}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{profile.display_name}さん、初めまして！\nまずはこちらから登録をお願いします👇\n{register_url}")
        )
        return

    # 占いリクエスト処理
    if "今日の運勢" in user_message:
        profile = user_profiles.get(user_id)
        if not profile:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="先に登録をお願いします！"))
            return
        prompt = f"{profile['name']}さん（{profile['birthday']}生まれ）の今日の運勢を占ってください。"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message["content"]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="「今日の運勢」と送ってみてください☀️"))

@app.route("/submit", methods=["POST"])
def submit():
    # フォームから登録情報を受け取り、user_profiles に保存
    name = request.form.get("name")
    birthday = request.form.get("birthday")
    user_id = request.form.get("user_id")
    # 画像アップロード処理は省略（前のコードを参照）

    # 仮保存（本番ではスプシ or DB）
    user_profiles[user_id] = {
        "name": name,
        "birthday": birthday,
        # "image_url": 保存したURLなど
    }

    return f"登録ありがとうございました！{name}さん"

@app.route("/register")
def register():
    user_id = request.args.get("uid", "")
    return render_template("register.html", user_id=user_id)

@app.route("/")
def home():
    return "Fortune bot system is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Renderが指定するポート番号に対応
    app.run(host="0.0.0.0", port=port, debug=True)

