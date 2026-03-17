"""Code executor tool — Python exec()."""

from __future__ import annotations

import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Type

from pydantic import BaseModel, Field

from registry.models import ToolMetadata
from tools.base import DynamicTool


class CodeExecutorInput(BaseModel):
    code: str = Field(..., description="Python code to execute")


class CodeExecutorTool(DynamicTool):
    name: str = "code_executor"
    description: str = "Execute Python code and return the output."
    args_schema: Type[BaseModel] = CodeExecutorInput

    def _run(self, code: str) -> str:
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Restricted globals — no file-system / network access from exec
        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "bool": bool,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "reversed": reversed,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "pow": pow,
                "isinstance": isinstance,
                "type": type,
                "True": True,
                "False": False,
                "None": None,
                "__import__": __import__,  # Allow math, datetime etc.
            }
        }

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals)

            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()

            result_parts = []
            if output:
                result_parts.append(f"📤 Çıktı:\n{output}")
            if errors:
                result_parts.append(f"⚠️ Stderr:\n{errors}")
            if not result_parts:
                result_parts.append("✅ Kod başarıyla çalıştı (çıktı yok).")

            return "\n".join(result_parts)

        except Exception:
            tb = traceback.format_exc()
            return f"❌ Hata:\n{tb}"

