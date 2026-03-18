"""Translation tool — deep-translator library."""

from __future__ import annotations

from typing import Type

from pydantic import BaseModel, Field

from registry.models import ToolMetadata
from tools.base import DynamicTool


class TranslateInput(BaseModel):
    text: str = Field(..., description="Text to translate")
    dest: str = Field(default="tr", description="Target language code, e.g. 'en', 'tr', 'de'")
    src: str = Field(default="auto", description="Source language code or 'auto' for detection")


class TranslateTool(DynamicTool):
    name: str = "translate"
    description: str = "Translate text between languages using Google Translate."
    args_schema: Type[BaseModel] = TranslateInput

    def _run(self, text: str, dest: str = "tr", src: str = "auto") -> str:
        try:
            from deep_translator import GoogleTranslator

            translated = GoogleTranslator(source=src, target=dest).translate(text)

            return (
                f"🌐 Çeviri ({src} → {dest})\n"
                f"   Kaynak: {text}\n"
                f"   Çeviri: {translated}"
            )
        except Exception as e:
            return f"Çeviri başarısız: {e}"