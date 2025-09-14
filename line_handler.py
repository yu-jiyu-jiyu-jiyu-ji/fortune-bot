import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from sheets import (
    can_ask_fortune_today,
    get_user_profile,
    increment_fortune_count
)
from openai_util import generate_fortune

# 環境変数からトークンを取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# メッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text

    print(f"📩 メッセージ受信: {message_text}")
    print(f"👤 ユーザーID: {user_id}")

    # 初回あいさつ・登録誘導
    if message_text in ["こんにちは", "はじめまして"]:
        register_url = f"https://fortune-bot-p2ey.onrender.com/register?uid={user_id}"
        reply = f"{user_id}さん、はじめまして！\nまずはこちらから登録をお願いします👇\n{register_url}"

    # 今日の運勢
    elif message_text == "今日の運勢":
        if can_ask_fortune_today(user_id):
            profile = get_user_profile(user_id)
            print(f"🧾 プロフィール取得: {profile}")

            if profile and "name" in profile and "birthday" in profile:
                name = profile["name"] or "あなた"
                birthday = profile["birthday"]
                # OpenAIで占い生成
                fortune = generate_fortune(name, birthday)
                increment_fortune_count(user_id)
                reply = f"{name}さんの今日の運勢は…\n\n{fortune}"
            else:
                reply = "登録情報が不十分です。\nもう一度登録をお願いします。"
        else:
            reply = "本日はすでに運勢をお届け済みです！\n明日またお試しください🌟"

    else:
        reply = "メッセージを受け取りました！\n「今日の運勢」と送ると、運勢をお伝えします✨"

    # LINEに返信
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )
    except Exception as e:
        print(f"⚠️ LINE返信エラー: {e}")
