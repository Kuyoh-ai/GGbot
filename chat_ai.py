# chat_ai.py
import os
import google.generativeai as genai
from typing import List
from PIL import Image
from io import BytesIO


class ChatAI:
    def __init__(
        self, api_key: str, model: str, system_prompt: str, error_message: str
    ):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.system_prompt = system_prompt
        self.error_message = error_message

    def generate_response(
        self, user_content: str, user_name: str, images: List[Image.Image]
    ) -> (int, str):
        """
        user_content: メンションやリプライを除去したユーザーからのテキスト
        images: PIL.Imageインスタンスを格納したリスト
        戻り値: (status_code, response_text)
        """

        prompt = (
            self.system_prompt
            + "\n"
            + user_name
            + " さんからのリクエスト: "
            + user_content
        )

        # 引数として渡すリストを構築
        # 最初の要素がprompt、続いて画像を並べる
        # 画像がない場合は単純にpromptを文字列として渡す
        try:
            if images:
                request_args = [prompt] + images
            else:
                request_args = prompt

            response = self.model.generate_content(request_args)
            return (200, response.text)
        except Exception:
            # エラーが起きた場合
            return (500, self.error_message)
