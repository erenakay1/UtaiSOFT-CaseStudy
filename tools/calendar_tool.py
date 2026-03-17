"""Google Calendar tool — Google Calendar API (OAuth 2.0)."""

from __future__ import annotations

import datetime
from typing import Type

from pydantic import BaseModel, Field

import config
from registry.models import ToolMetadata
from tools.base import DynamicTool


class CalendarInput(BaseModel):
    action: str = Field(
        ...,
        description="Action: 'list' to show upcoming events, 'create' to add a new event",
    )
    summary: str = Field(default="", description="Event title (for create)")
    start_time: str = Field(
        default="",
        description="Event start time in ISO format, e.g. '2024-12-25T10:00:00' (for create)",
    )
    end_time: str = Field(
        default="",
        description="Event end time in ISO format (for create)",
    )
    max_results: int = Field(default=5, description="Number of events to list (for list)")


def _get_calendar_service():
    """Build and return an authenticated Google Calendar service."""
    import os
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/calendar"]
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

    return build("calendar", "v3", credentials=creds)


class CalendarTool(DynamicTool):
    name: str = "calendar"
    description: str = "Manage Google Calendar events — list or create events."
    args_schema: Type[BaseModel] = CalendarInput

    def _run(
        self,
        action: str,
        summary: str = "",
        start_time: str = "",
        end_time: str = "",
        max_results: int = 5,
    ) -> str:
        try:
            service = _get_calendar_service()

            if action == "list":
                now = datetime.datetime.utcnow().isoformat() + "Z"
                events_result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=now,
                        maxResults=max_results,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )
                events = events_result.get("items", [])

                if not events:
                    return "📅 Yaklaşan etkinlik bulunamadı."

                lines = ["📅 Yaklaşan Etkinlikler:\n"]
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    lines.append(f"  • {event['summary']} — {start}")
                return "\n".join(lines)

            elif action == "create":
                if not summary or not start_time or not end_time:
                    return "Etkinlik oluşturmak için summary, start_time ve end_time gerekli."

                event = {
                    "summary": summary,
                    "start": {"dateTime": start_time, "timeZone": "Europe/Istanbul"},
                    "end": {"dateTime": end_time, "timeZone": "Europe/Istanbul"},
                }
                created = service.events().insert(calendarId="primary", body=event).execute()
                return f"✅ Etkinlik oluşturuldu: {created['summary']} ({created.get('htmlLink', '')})"

            else:
                return f"Bilinmeyen aksiyon: {action}. 'list' veya 'create' kullanın."

        except Exception as e:
            return f"Takvim hatası: {e}"

