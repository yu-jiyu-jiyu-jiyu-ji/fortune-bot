import openai
import os

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# 占いメッセージを生成する関数
def generate_fortune(name, birthday):
    prompt = f"""
以下は、占い師が依頼者の運勢を占う内容です。

【名前】：{name}
【生年月日】：{birthday}

この情報を元にして、今日の運勢を以下の構成で出力してください。

---
◆全体運（5段階で運勢評価とその根拠）
◆恋愛運（5段階で運勢評価とアドバイス）
◆仕事運（5段階で運勢評価とアドバイス）
◆ラッキーアイテム
---

ですます調で200文字以内に収めて、柔らかく肯定的な口調で返してください。
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # 必要に応じて gpt-3.5-turbo に変更可能
            messages=[
                {"role": "system", "content": "あなたは優しい占い師です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300,
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "エラーが発生しました。もう一度お試しください。"
