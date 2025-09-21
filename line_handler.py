from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import date
import os

from sheets import get_user_profile, update_user_fortune
from openai_util import generate_fortune

# LINE API
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))


# ===============================
# LINE メッセージイベント処理
# ===============================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text.strip()

    if message_text == "今日の運勢":
        profile = get_user_profile(user_id)
        if not profile:
            reply_text = "まずはプロフィール登録をお願いします🙏"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        today = date.today()
        last_date = profile["last_fortune_date"]

        # ===============================
        # 1日の利用制限チェック
        # ===============================
        if last_date == today and profile["count_today"] >= profile["limit"]:
            reply_text = "本日はすでに運勢をお届け済みです！\n明日またお試しください🌟"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        # ===============================
        # 占い生成
        # ===============================
        fortune_text = generate_fortune(profile["name"], profile["birthday"])

        if "エラー" in fortune_text:
            reply_text = "占いの生成に失敗しました。時間をおいて再度お試しください🙏"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        # ===============================
        # 利用回数更新
        # ===============================
        if last_date == today:
            new_count = profile["count_today"] + 1
        else:
            new_count = 1

        update_user_fortune(user_id, today, new_count)

        # ===============================
        # LINEへ返信
        # ===============================
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fortune_text))
