from flask import request, redirect, render_template
from sheets import append_user_data
from drive import save_images_to_drive

# `/submit` の POST 処理
def handle_form_submission():
    try:
        # フォームデータの取得
        user_id = request.form.get("user_id")
        name = request.form.get("name")
        birthday = request.form.get("birthday")
        left_hand = request.files.get("left_hand")
        right_hand = request.files.get("right_hand")

        print(f"📥 受信フォームデータ: user_id={user_id}, name={name}, birthday={birthday}")

        # Google Drive に画像保存（userId フォルダに上書き保存）
        try:
            print("📸 画像保存開始")
            save_images_to_drive(user_id, {
                "Lhand.png": left_hand,
                "Rhand.png": right_hand
            })
            print("✅ 画像保存完了")
        except Exception as img_err:
            print(f"❌ 画像保存エラー: {img_err}")

        # スプレッドシートにユーザ情報を保存
        try:
            print("📝 スプレッドシート保存開始")
            append_user_data(user_id, name, birthday)
            print("✅ スプレッドシート保存完了")
        except Exception as sheet_err:
            print(f"❌ スプレッドシート保存エラー: {sheet_err}")
            return render_template("error.html", message="スプレッドシートへの保存に失敗しました。")

        # 完了後、thanksページにリダイレクト
        return redirect("/thanks")

    except Exception as e:
        print(f"❌ フォーム送信処理全体でエラー: {e}")
        return render_template("error.html", message="登録処理中にエラーが発生しました。")
