from __future__ import annotations

"""
LLM provider abstractions used to keep Mangaba agnostic to any specific vendor.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, Type


@dataclass
class LLMResponse:
    """Resposta padronizada de um LLM."""

    text: str
    raw: Any = None


class BaseLLMProvider:
    """Interface básica para provedores de LLM."""

    name: str = "base"
    aliases: Tuple[str, ...] = ()

    def __init__(self, api_key: str, model: str, **options: Any) -> None:
        self.api_key = api_key
        self.model = model
        self.options = options or {}

    @classmethod
    def matches(cls, provider_name: str) -> bool:
        normalized = provider_name.lower()
        return normalized == cls.name or normalized in cls.aliases

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:  # pragma: no cover - interface
        raise NotImplementedError


class GoogleLLMProvider(BaseLLMProvider):
    """Provider para Google Gemini / Google AI Studio."""

    name = "google"
    aliases = ("gemini", "google-ai", "googleai")

    def __init__(self, api_key: str, model: str, **options: Any) -> None:
        super().__init__(api_key, model, **options)
        try:
            import google.generativeai as genai  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependência externa
            raise ImportError(
                "Pacote 'google-generativeai' não encontrado. "
                "Instale com 'pip install google-generativeai'."
            ) from exc

        genai.configure(api_key=api_key)
        generation_config = options.get("generation_config")
        safety_settings = options.get("safety_settings")
        if generation_config is None:
            generation_config = {
                key: options.get(key)
                for key in ("temperature", "top_p", "top_k", "max_output_tokens")
                if options.get(key) is not None
            } or None

        self._model = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        response = self._model.generate_content(prompt, **{k: v for k, v in kwargs.items() if v is not None})
        text = getattr(response, "text", None) or ""
        return LLMResponse(text=text, raw=response)


class OpenAILLMProvider(BaseLLMProvider):
    """Provider para modelos da OpenAI."""

    name = "openai"
    aliases = ("gpt", "chatgpt")

    def __init__(self, api_key: str, model: str, **options: Any) -> None:
        super().__init__(api_key, model, **options)
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependência externa
            raise ImportError(
                "Pacote 'openai' não encontrado. Instale com 'pip install openai'."
            ) from exc

        self._client = OpenAI(api_key=api_key)
        self._temperature = options.get("temperature", 0.7)
        self._max_tokens = options.get("max_output_tokens", 1024)
        self._system_prompt = options.get("system_prompt")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        temperature = kwargs.get("temperature", self._temperature)
        max_tokens = kwargs.get("max_output_tokens", self._max_tokens)
        system_prompt = kwargs.get("system_prompt", self._system_prompt)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        text = response.choices[0].message.content or ""
        return LLMResponse(text=text, raw=response)


class AnthropicLLMProvider(BaseLLMProvider):
    """Provider para modelos da Anthropic (Claude)."""

    name = "anthropic"
    aliases = ("claude",)

    def __init__(self, api_key: str, model: str, **options: Any) -> None:
        super().__init__(api_key, model, **options)
        try:
            from anthropic import Anthropic  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependência externa
            raise ImportError(
                "Pacote 'anthropic' não encontrado. Instale com 'pip install anthropic'."
            ) from exc

        self._client = Anthropic(api_key=api_key)
        self._temperature = options.get("temperature", 0.7)
        self._max_tokens = options.get("max_output_tokens", 1024)
        self._system_prompt = options.get("system_prompt")

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        temperature = kwargs.get("temperature", self._temperature)
        max_tokens = kwargs.get("max_output_tokens", self._max_tokens)
        system_prompt = kwargs.get("system_prompt", self._system_prompt)

        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )

        parts = []
        for item in response.content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
        return LLMResponse(text="\n".join(parts), raw=response)


class HuggingFaceLLMProvider(BaseLLMProvider):
    """Provider para modelos hospedados no Hugging Face Hub."""

    name = "huggingface"
    aliases = ("hf", "hugging-face")

    def __init__(self, api_key: str, model: str, **options: Any) -> None:
        super().__init__(api_key, model, **options)
        try:
            from huggingface_hub import InferenceClient  # type: ignore
        except ImportError as exc:  # pragma: no cover - dependência externa
            raise ImportError(
                "Pacote 'huggingface-hub' não encontrado. Instale com 'pip install huggingface-hub'."
            ) from exc

        self._client = InferenceClient(token=api_key)
        self._temperature = options.get("temperature", 0.7)
        self._max_tokens = options.get("max_output_tokens", 512)

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        temperature = kwargs.get("temperature", self._temperature)
        max_tokens = kwargs.get("max_output_tokens", self._max_tokens)

        response = self._client.text_generation(
            prompt,
            model=self.model,
            max_new_tokens=max_tokens,
            temperature=temperature,
            return_full_text=False,
        )

        if isinstance(response, str):
            text = response
        else:
            text = response.get("generated_text") or ""

        return LLMResponse(text=text, raw=response)


PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
    GoogleLLMProvider.name: GoogleLLMProvider,
    OpenAILLMProvider.name: OpenAILLMProvider,
    AnthropicLLMProvider.name: AnthropicLLMProvider,
    HuggingFaceLLMProvider.name: HuggingFaceLLMProvider,
}


def _resolve_provider_class(provider_name: str) -> Type[BaseLLMProvider]:
    normalized = provider_name.lower()
    for name, provider_cls in PROVIDERS.items():
        if provider_cls.matches(normalized):
            return provider_cls
    raise ValueError(
        f"Provedor LLM '{provider_name}' não suportado. "
        f"Opções válidas: {', '.join(sorted(set(PROVIDERS.keys())))}"
    )


class LLMClient:
    """Cliente de alto nível para qualquer LLM suportado."""

    def __init__(self, provider: str, api_key: str, model: str, **options: Any) -> None:
        provider_cls = _resolve_provider_class(provider)
        self.provider_name = provider_cls.name
        self._provider = provider_cls(api_key=api_key, model=model, **options)

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        return self._provider.generate(prompt, **kwargs)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return self.generate(prompt, **kwargs).text


def create_llm_client(provider: str, api_key: str, model: str, **options: Any) -> LLMClient:
    """Convenience helper para criar clientes LLM."""
    if not provider:
        raise ValueError("O nome do provedor LLM é obrigatório")
    if not api_key:
        raise ValueError("API key é obrigatória para inicializar o provedor LLM")
    if not model:
        raise ValueError("Nome do modelo é obrigatório")
    return LLMClient(provider=provider, api_key=api_key, model=model, **options)


def get_supported_providers() -> Tuple[str, ...]:
    """Retorna lista de provedores suportados."""
    aliases = set()
    for provider_cls in PROVIDERS.values():
        aliases.add(provider_cls.name)
        aliases.update(provider_cls.aliases)
    return tuple(sorted(aliases))
