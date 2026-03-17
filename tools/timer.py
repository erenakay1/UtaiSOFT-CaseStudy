"""Timer / Alarm tool — APScheduler."""

from __future__ import annotations

import datetime
import threading
from typing import Type

from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel, Field

from registry.models import ToolMetadata
from tools.base import DynamicTool

# Shared scheduler instance
_scheduler: BackgroundScheduler | None = None
_scheduler_lock = threading.Lock()
_active_timers: dict[str, dict] = {}


def _get_scheduler() -> BackgroundScheduler:
    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            _scheduler = BackgroundScheduler()
            _scheduler.start()
    return _scheduler


class TimerInput(BaseModel):
    action: str = Field(
        ...,
        description="Action: 'set' to create a timer, 'list' to show active timers, 'cancel' to cancel a timer",
    )
    name: str = Field(default="timer", description="Timer name / label")
    seconds: int = Field(default=0, description="Duration in seconds (for set)")
    timer_id: str = Field(default="", description="Timer ID to cancel (for cancel)")


class TimerTool(DynamicTool):
    name: str = "timer"
    description: str = "Set timers and alarms using APScheduler."
    args_schema: Type[BaseModel] = TimerInput

    def _run(
        self,
        action: str,
        name: str = "timer",
        seconds: int = 0,
        timer_id: str = "",
    ) -> str:
        try:
            scheduler = _get_scheduler()

            if action == "set":
                if seconds <= 0:
                    return "Geçerli bir süre belirtin (seconds > 0)."

                fire_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                job_id = f"timer_{name}_{id(fire_time)}"

                def _on_fire():
                    print(f"\n⏰ ALARM: '{name}' süresi doldu!")
                    _active_timers.pop(job_id, None)

                scheduler.add_job(
                    _on_fire,
                    "date",
                    run_date=fire_time,
                    id=job_id,
                )

                _active_timers[job_id] = {
                    "name": name,
                    "fire_time": fire_time.isoformat(),
                    "seconds": seconds,
                }

                return (
                    f"⏱ Timer ayarlandı!\n"
                    f"   İsim: {name}\n"
                    f"   Süre: {seconds} saniye\n"
                    f"   Çalacağı an: {fire_time.strftime('%H:%M:%S')}\n"
                    f"   ID: {job_id}"
                )

            elif action == "list":
                if not _active_timers:
                    return "⏱ Aktif timer bulunmuyor."

                lines = ["⏱ Aktif Timer'lar:\n"]
                for tid, info in _active_timers.items():
                    lines.append(
                        f"  • {info['name']} — {info['seconds']}s "
                        f"(çalacak: {info['fire_time']}) [ID: {tid}]"
                    )
                return "\n".join(lines)

            elif action == "cancel":
                if not timer_id:
                    return "İptal için timer_id gerekli."

                try:
                    scheduler.remove_job(timer_id)
                    info = _active_timers.pop(timer_id, {})
                    return f"🛑 Timer iptal edildi: {info.get('name', timer_id)}"
                except Exception:
                    return f"Timer bulunamadı: {timer_id}"

            else:
                return f"Bilinmeyen aksiyon: {action}. 'set', 'list', veya 'cancel' kullanın."

        except Exception as e:
            return f"Timer hatası: {e}"

