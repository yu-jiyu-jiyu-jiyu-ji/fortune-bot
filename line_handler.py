import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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

    if message_text in ["こんにちは", "はじめまして"]:
        register_url = f"https://fortune-bot-p2ey.onrender.com/register?uid={user_id}"
        reply = f"{user_id}さん、初めまして！\nまずはこちらから登録をお願いします👇\n{register_url}"
    elif message_text == "今日の運勢":
        from openai_util import get_fortune_result
        from sheets import can_ask_fortune_today

        if can_ask_fortune_today(user_id):
            fortune = get_fortune_result(user_id)
            reply = f"{user_id}さんの今日の運勢は…\n\n{fortune}"
        else:
            reply = "本日はすでに運勢をお届け済みです！明日またお試しください🌟"
    else:
        reply = "メッセージを受け取りました！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
