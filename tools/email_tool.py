"""Email tool — Gmail API (OAuth 2.0)."""

from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText
from typing import Type

from pydantic import BaseModel, Field

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


class EmailInput(BaseModel):
    action: str = Field(
        ...,
        description="Action: 'send' to send an email, 'read' to read recent emails",
    )
    to: str = Field(default="", description="Recipient email address (for send)")
    subject: str = Field(default="", description="Email subject (for send)")
    body: str = Field(default="", description="Email body text (for send)")
    max_results: int = Field(default=5, description="Number of emails to read (for read)")


def _get_gmail_service():
    """Build and return an authenticated Gmail service."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]
    creds = None

    if os.path.exists(config.GOOGLE_TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_PATH, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_CREDENTIALS_PATH, scopes
            )
            creds = flow.run_local_server(port=0)
        with open(config.GOOGLE_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


class EmailTool(DynamicTool):
    name: str = "email"
    description: str = "Send and read emails using Gmail API."
    args_schema: Type[BaseModel] = EmailInput

    def _run(
        self,
        action: str,
        to: str = "",
        subject: str = "",
        body: str = "",
        max_results: int = 5,
    ) -> str:
        try:
            service = _get_gmail_service()

            if action == "send":
                if not to or not subject or not body:
                    return "E-posta göndermek için 'to', 'subject' ve 'body' gerekli."

                message = MIMEText(body)
                message["to"] = to
                message["subject"] = subject
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
                send_body = {"raw": raw}
                service.users().messages().send(userId="me", body=send_body).execute()
                return f"✉️ E-posta gönderildi → {to} (Konu: {subject})"

            elif action == "read":
                results = (
                    service.users()
                    .messages()
                    .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
                    .execute()
                )
                messages = results.get("messages", [])

                if not messages:
                    return "📭 Gelen kutusunda e-posta bulunamadı."

                lines = ["📬 Son E-postalar:\n"]
                for msg_ref in messages:
                    msg = (
                        service.users()
                        .messages()
                        .get(userId="me", id=msg_ref["id"], format="metadata")
                        .execute()
                    )
                    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                    frm = headers.get("From", "Bilinmeyen")
                    subj = headers.get("Subject", "(Konu yok)")
                    lines.append(f"  • Gönderen: {frm}\n    Konu: {subj}")

                return "\n".join(lines)

            else:
                return f"Bilinmeyen aksiyon: {action}. 'send' veya 'read' kullanın."

        except Exception as e:
            return f"E-posta hatası: {e}"

