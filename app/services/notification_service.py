from __future__ import annotations

from typing import Literal

from app.schemas.communication_schema import TwilioActionResult
from app.services.twilio_service import TwilioService, get_twilio_service


Priority = Literal["LOW", "MEDIUM", "HIGH"]


class NotificationService:
    """Twilio-backed notification flows for SMS and voice calls."""

    @staticmethod
    def unique_recipients(phone_numbers: list[str]) -> list[str]:
        deduped: list[str] = []
        seen: set[str] = set()
        for number in phone_numbers:
            normalized = number.strip()
            if normalized and normalized not in seen:
                deduped.append(normalized)
                seen.add(normalized)
        return deduped

    def send_sms_batch(
        self,
        phone_numbers: list[str],
        message: str,
        twilio_service: TwilioService | None = None,
    ) -> list[TwilioActionResult]:
        service = twilio_service or get_twilio_service()
        recipients = self.unique_recipients(phone_numbers)
        return [service.send_sms(number, message) for number in recipients]

    def make_call_batch(
        self,
        phone_numbers: list[str],
        message: str,
        sound_url: str | None = None,
        voice: str = "alice",
        language: str | None = None,
        twilio_service: TwilioService | None = None,
    ) -> list[TwilioActionResult]:
        service = twilio_service or get_twilio_service()
        recipients = self.unique_recipients(phone_numbers)
        return [
            service.make_call(number, message, sound_url, voice, language)
            for number in recipients
        ]

    def notify_by_priority(
        self,
        priority: Priority,
        phone_numbers: list[str],
        message: str,
        sound_url: str | None = None,
        voice: str = "alice",
        language: str | None = None,
        twilio_service: TwilioService | None = None,
    ) -> tuple[list[TwilioActionResult], list[TwilioActionResult]]:
        sms_results = self.send_sms_batch(
            phone_numbers=phone_numbers,
            message=message,
            twilio_service=twilio_service,
        )

        call_results: list[TwilioActionResult] = []
        if priority != "LOW":
            call_results = self.make_call_batch(
                phone_numbers=phone_numbers,
                message=message,
                sound_url=sound_url,
                voice=voice,
                language=language,
                twilio_service=twilio_service,
            )

        return sms_results, call_results


notification_service = NotificationService()
