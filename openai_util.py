import os
import openai

openai.api_key = os.getenv("OPENAI_APIKEY")


def generate_fortune(name, birthday, mode="today", face_image="", right_hand="", left_hand=""):
    """
    mode に応じてプロンプトを切り替える
    - "today" : 今日の運勢
    - "palm"  : 手相
    - "face"  : 顔相
    """

    if mode == "today":
        prompt = f"""
{name}さん（{birthday}生まれ）の、今日の運勢を詳しく教えてください。

    以下の6つの項目を、それぞれ **80文字前後** で書いてください：
    - 総合運
    - 恋愛運
    - 仕事運
    - 金運
    - 健康運
    - 今日の一言アドバイス

    条件：
    - 各項目は必ず見出しをつける
    - 前向きで具体的
    - 読みやすい文体
    - 出力はMarkdown形式
"""

    elif mode == "palm":
        prompt = f"""
{name}さんの手相占いをしてください。
右手: {right_hand or "未提供"}
左手: {left_hand or "未提供"}

以下の4項目を80文字前後でまとめてください：
- 性格や強み
- 仕事運の特徴
- 恋愛傾向
- 今日のアドバイス
"""

    elif mode == "face":
        prompt = f"""
{name}さんの顔相占いをしてください。
顔画像: {face_image or "未提供"}

以下の3項目を80文字前後でまとめてください：
- 性格や印象
- 今後の運勢
- 今日のアドバイス
"""

    else:
        prompt = f"{name}さんの運勢を占ってください。"

    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは優しい日本語の占い師です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=700,
        )
        return res["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "エラーが発生しました。もう一度お試しください。"
