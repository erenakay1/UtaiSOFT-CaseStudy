"""Document reader tool — pypdf + requests."""

from __future__ import annotations

import io
import tempfile
from typing import Type
from pathlib import Path

import requests
from pydantic import BaseModel, Field

from registry.models import ToolMetadata
from tools.base import DynamicTool


class DocumentReaderInput(BaseModel):
    source: str = Field(
        ...,
        description="URL or local file path to a PDF or TXT document",
    )
    max_chars: int = Field(
        default=3000,
        description="Maximum characters to return from the document",
    )


class DocumentReaderTool(DynamicTool):
    name: str = "document_reader"
    description: str = "Read and extract text from PDF or TXT documents (URL or local file)."
    args_schema: Type[BaseModel] = DocumentReaderInput

    def _run(self, source: str, max_chars: int = 3000) -> str:
        try:
            # Determine if source is a URL or local path
            if source.startswith(("http://", "https://")):
                content = self._read_from_url(source)
            else:
                content = self._read_from_file(source)

            if len(content) > max_chars:
                content = content[:max_chars] + f"\n\n... (toplam {len(content)} karakter, {max_chars} gösteriliyor)"

            return f"📄 Belge İçeriği:\n\n{content}"

        except Exception as e:
            return f"Belge okuma hatası: {e}"

    def _read_from_url(self, url: str) -> str:
        """Download and parse a document from a URL."""
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "")

        if "pdf" in content_type or url.lower().endswith(".pdf"):
            return self._parse_pdf(io.BytesIO(resp.content))
        else:
            # Assume text (TXT, HTML, etc.)
            return resp.text

    def _read_from_file(self, path: str) -> str:
        """Read a document from a local file path."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")

        if p.suffix.lower() == ".pdf":
            with open(p, "rb") as f:
                return self._parse_pdf(f)
        else:
            return p.read_text(encoding="utf-8", errors="replace")

    def _parse_pdf(self, file_obj) -> str:
        """Extract text from a PDF file object."""
        from pypdf import PdfReader

        reader = PdfReader(file_obj)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages.append(f"--- Sayfa {i + 1} ---\n{text}")
        return "\n\n".join(pages) if pages else "(PDF'den metin çıkarılamadı)"

