# chat_ai.py
"""
openai‑1.75.0 で Grok 3 に問い合わせるユーティリティ

・ChatCompletion を使用
・画像付きプロンプト（Vision）にも対応
・(status_code, response_text) を返すインターフェースはそのまま維持
"""
from __future__ import annotations

import base64
import io
from typing import List, Tuple

from PIL import Image
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class ChatAI:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        error_message: str,
    ) -> None:
        """
        Parameters
        ----------
        api_key : str
            OpenAI (or Grok3 エンドポイント) の API キー
        model : str
            利用するモデル名 (例: "grok‑3")
        system_prompt : str
            システムメッセージとして与えるプロンプト
        error_message : str
            想定外エラー時に返すメッセージ
        """
        self.client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
        self.model = model
        self.system_prompt = system_prompt
        self.error_message = error_message

    # --------------------------------------------------------------------- #
    # public
    # --------------------------------------------------------------------- #
    def generate_response(
        self,
        user_content: str,
        user_name: str,
        images: List[Image.Image] | None,
    ) -> Tuple[int, str]:
        """
        Parameters
        ----------
        user_content : str
            メンションやリプライを除去したユーザー入力
        user_name : str
            発話者名（ログ用途）
        images : list[PIL.Image.Image] | None
            画像入力。空ならテキストのみ

        Returns
        -------
        (status_code, response_text) : (int, str)
            200 = 正常応答, 500 = 例外
        """
        try:
            messages = self._build_messages(user_content, user_name, images)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return 200, response.choices[0].message.content  # type: ignore[attr-defined]
        except Exception as e:
            print(e)
            return 500, self.error_message

    # --------------------------------------------------------------------- #
    # private helpers
    # --------------------------------------------------------------------- #
    def _build_messages(
        self,
        user_content: str,
        user_name: str,
        images: List[Image.Image] | None,
    ) -> List[ChatCompletionMessageParam]:
        """OpenAI ChatCompletion 用 message 配列を構築"""
        # ----- system -----
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.system_prompt}
        ]

        # ----- user -----
        user_parts: list[dict] = [
            {
                "type": "text",
                "text": f"{user_name} さんからのリクエスト: {user_content}",
            }
        ]

        if images:
            user_parts += [self._pil_to_part(img) for img in images]

        messages.append({"role": "user", "content": user_parts})
        return messages

    @staticmethod
    def _pil_to_part(img: Image.Image) -> dict:
        """
        PIL.Image → Vision API 用 image_url‑part に変換（base64 DataURL）
        ※ JPEG で再エンコードし品質を 85 % に設定
        """
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        data_url = f"data:image/jpeg;base64,{b64}"
        return {"type": "image_url", "image_url": {"url": data_url}}
