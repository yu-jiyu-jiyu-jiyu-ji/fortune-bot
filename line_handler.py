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
        from sheets import get_user_info, update_last_fortune_timestamp
        from openai_util import generate_fortune

        try:
            # スプレッドシートからユーザー情報取得
            user_info = get_user_info(user_id)
            if not user_info:
                reply = "ごめんなさい。まだ登録されていないようです。先に登録をお願いします！"
            else:
                name = user_info.get("name")
                birthday = user_info.get("birthday")

                # OpenAIで占い生成
                fortune = generate_fortune(name, birthday)

                # 返信文作成
                reply = f"{name}さんの今日の運勢は…\n\n{fortune}"

                # 最終占い日を更新
                update_last_fortune_timestamp(user_id)

        except Exception as e:
            print(f"占い処理中にエラー: {e}")
            reply = "エラーが発生しました。もう一度お試しください🙏"

    else:
        reply = "メッセージを受け取りました！「今日の運勢」と送ってみてください🌟"

    # LINEへ返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
