import os
import base64
import google.generativeai as genai


class ChatAI:
    def __init__(
        self, api_key: str, model: str, system_prompt: str, error_message: str
    ):
        genai.configure(api_key=api_key)
        self.system_prompt = system_prompt
        self.error_message = error_message
        self.model = genai.GenerativeModel(model)

    def generate_response(
        self, user_content: str, attachments: list[bytes]
    ) -> (int, str):
        """
        user_content: メンションやリプライを除去したユーザーからのテキスト
        attachments: base64デコード済みのバイナリデータを格納したリスト
        戻り値: (status_code, response_text)
        status_codeは暫定的に200固定も可(エラーハンドリングを拡張したければここで対応)
        """

        # 画像等の添付ファイルを元にプロンプトを拡張する例(適宜実装)
        # 一例として、画像があれば説明を求めるメッセージをsystem promptに付け足す
        prompt = self.system_prompt + "\nユーザーからのリクエスト: " + user_content
        if attachments:
            prompt += f"\n(以下はユーザーが添付したファイルデータに関する質問です: {len(attachments)}ファイル)"

        try:
            response = self.model.generate_content(prompt)
            return (200, response.text)
        except Exception:
            # エラーが起きた場合
            return (500, self.error_message)
