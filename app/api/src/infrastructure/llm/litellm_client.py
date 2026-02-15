"""LiteLLMクライアント実装."""

import json

import litellm

from src.core.config import settings
from src.domain.services.llm_client import LLMClient, LLMResponse


class LiteLLMClient(LLMClient):
    """LiteLLMを使用したLLMクライアント.

    OpenAI互換APIを通じて様々なLLMにアクセスする。
    """

    def __init__(
        self,
        api_base: str | None = None,
        model_name: str | None = None,
    ):
        """初期化.

        Args:
            api_base: APIベースURL（デフォルトは設定から）
            model_name: モデル名（デフォルトは設定から）
        """
        self._api_base = api_base or settings.llm_api_base
        self._model_name = model_name or settings.llm_model_name

    async def generate(
        self, prompt: str, system_prompt: str | None = None
    ) -> LLMResponse:
        """テキストを生成する.

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）

        Returns:
            LLMレスポンス
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await litellm.acompletion(
            model=self._model_name,
            messages=messages,
            api_base=self._api_base,
        )

        content = response.choices[0].message.content
        return LLMResponse(content=content, model=self._model_name)

    async def generate_json(
        self, prompt: str, system_prompt: str | None = None
    ) -> dict:
        """JSON形式でテキストを生成する.

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）

        Returns:
            パースされたJSON辞書
        """
        # JSONを要求するプロンプトを追加
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."

        response = await self.generate(json_prompt, system_prompt)

        # JSONをパース（コードブロックがある場合は除去）
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)
