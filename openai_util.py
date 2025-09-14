import openai
import os

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 占いメッセージを生成する関数
def generate_fortune(name, birthday):
    prompt = f"""
{name}さん（{birthday}生まれ）の、今日（2025年9月14日）の運勢を教えてください。

以下の6項目について、それぞれ**日本語で80文字前後**（±5字程度）でまとめてください：

- 総合運
- 恋愛運
- 仕事運
- 金運
- 健康運
- 今日の一言アドバイス

出力条件：
- 内容は前向きで具体性があるもの
- 読みやすく自然な文体（親しみやすく肯定的）
- 各項目の前に絵文字＋見出し（例：🔮 総合運）を付けること
- 出力形式は **Markdown形式**

# 出力例（フォーマット参考）
🔮 総合運  
〜本文80文字〜

💖 恋愛運  
〜本文80文字〜

💼 仕事運  
〜本文80文字〜

💰 金運  
〜本文80文字〜

🧘‍♂️ 健康運  
〜本文80文字〜

🌟 今日の一言アドバイス  
〜本文80文字〜
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは優しい日本語の占い師です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500,
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "エラーが発生しました。もう一度お試しください。"
