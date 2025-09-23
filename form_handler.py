from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import date
import os

from sheets import get_user_profile, update_user_fortune, update_user_images
from openai_util import generate_fortune

# LINE API
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 登録フォームURL
REGISTER_FORM_URL = os.getenv("REGISTER_FORM_URL", "https://example.com/form")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text.strip()

    profile = get_user_profile(user_id)

    # ===============================
    # プロフィールが未登録の場合
    # ===============================
    if not profile:
        reply_text = f"まずはプロフィール登録をお願いします🙏\n{REGISTER_FORM_URL}\n\n※氏名と生年月日の変更はできません"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    today = date.today()
    last_date = profile["last_fortune_date"]

    # ===============================
    # 今日の運勢
    # ===============================
    if message_text == "今日の運勢":
        if last_date == today and profile["count_today"] >= profile["limit"]:
            reply_text = "本日はすでに運勢をお届け済みです！\n明日またお試しください🌟"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        fortune_text = generate_fortune(profile["name"], profile["birthday"], mode="today")

        if last_date == today:
            new_count = profile["count_today"] + 1
        else:
            new_count = 1
        update_user_fortune(user_id, today, new_count)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fortune_text))
        return

    # ===============================
    # 手相占い
    # ===============================
    if message_text == "手相":
        if not profile["right_hand"] and not profile["left_hand"]:
            reply_text = f"手の写真が未登録です📷\n以下のフォームから登録してください👇\n{REGISTER_FORM_URL}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        fortune_text = generate_fortune(profile["name"], profile["birthday"], mode="palm",
                                        right_hand=profile["right_hand"], left_hand=profile["left_hand"])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fortune_text))
        return

    # ===============================
    # 顔相占い
    # ===============================
    if message_text == "顔相":
        if not profile["face_image"]:
            reply_text = f"顔の写真が未登録です📷\n以下のフォームから登録してください👇\n{REGISTER_FORM_URL}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            return

        fortune_text = generate_fortune(profile["name"], profile["birthday"], mode="face",
                                        face_image=profile["face_image"])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fortune_text))
        return

    # ===============================
    # プロフィール編集
    # ===============================
    if message_text == "プロフィール":
        reply_text = f"プロフィール編集はこちらから👇\n{REGISTER_FORM_URL}\n\n※氏名・生年月日は変更できません。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return
