"""LiteLLMクライアント実装."""

import asyncio
import json
import logging
import re

import litellm

from src.core.config import settings
from src.domain.services.llm_client import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


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

    async def generate(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
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

        # api_base を指定している場合は OpenAI 互換として扱う（openai/ 必須）
        model = self._model_name
        if self._api_base and not model.startswith("openai/"):
            model = f"openai/{model.split('/')[-1]}" if "/" in model else f"openai/{model}"

        # カスタム api_base（LM Studio 等）ではAPIキー不要だが、
        # OpenAIクライアントが要求するためダミーを渡す
        kwargs = {"model": model, "messages": messages, "api_base": self._api_base}
        if self._api_base:
            kwargs["api_key"] = "lm-studio"

        # 接続エラー時は最大3回リトライ（400系はリトライしない）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await litellm.acompletion(**kwargs)
                content = response.choices[0].message.content
                return LLMResponse(content=content, model=self._model_name)
            except litellm.BadRequestError:
                # 400系（コンテキスト超過等）はリトライせず即座にraise
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = 2**attempt  # 1秒, 2秒, ...
                    logger.warning(
                        f"LLM呼び出し失敗 (試行{attempt + 1}/{max_retries}): "
                        f"{e}. {wait}秒後にリトライ"
                    )
                    await asyncio.sleep(wait)
                else:
                    raise

    async def generate_json(self, prompt: str, system_prompt: str | None = None) -> dict:
        """JSON形式でテキストを生成する.

        Args:
            prompt: ユーザープロンプト
            system_prompt: システムプロンプト（オプション）

        Returns:
            パースされたJSON辞書
        """
        json_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."

        max_retries = 3
        for attempt in range(max_retries):
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

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # LLMがLaTeX（\phi, \mathcal等）を含むJSONを返す場合、
                # 無効なエスケープシーケンスを修復してリトライ
                try:
                    fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", content)
                    return json.loads(fixed)
                except json.JSONDecodeError as e2:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"JSONパース失敗 (試行{attempt + 1}/{max_retries}): "
                            f"{e2}. リトライします"
                        )
                    else:
                        logger.error(
                            f"JSONパース失敗、リトライ上限到達。レスポンス: {content[:200]}"
                        )
                        raise
