from typing import Optional

from app.services.notification_service import notification_service
from app.services.twilio_service import get_twilio_service
from app.utils.communication_helpers import format_emergency_message
from app.utils.logger import logger


class AlertService:
    """Handle emergency alert actions based on severity."""

    @staticmethod
    def _build_recipients(
        doctor_number: Optional[str],
        family_numbers: list[str],
    ) -> list[str]:
        recipients = []
        if doctor_number:
            recipients.append(doctor_number)
        recipients.extend(family_numbers)
        return notification_service.unique_recipients(recipients)

    @staticmethod
    def _count_failed(results: list) -> int:
        return sum(1 for result in results if result.status == "failed")

    def process_alert(
        self,
        severity: str,
        patient_id: str,
        alert_type: str,
        location: dict,
        doctor_number: Optional[str] = None,
        family_numbers: Optional[list[str]] = None,
        custom_message: Optional[str] = None,
        sound_url: Optional[str] = None,
        voice: str = "alice",
        language: Optional[str] = None,
    ) -> list[str]:
        """Process alert based on severity: LOW=>SMS, otherwise SMS+CALL."""
        actions: list[str] = []
        recipients = self._build_recipients(doctor_number, family_numbers or [])

        if not recipients:
            logger.warning(
                "No emergency contacts provided for patient %s; skipping notifications",
                patient_id,
            )
            return ["No emergency contacts configured"]

        message = custom_message or format_emergency_message(
            patient_name=patient_id,
            emergency_type=alert_type,
            location=f"{location['lat']}, {location['lng']}",
        )

        try:
            twilio_service = get_twilio_service()
        except RuntimeError as exc:
            logger.error("Twilio configuration error: %s", str(exc))
            return [f"Notification failed: {str(exc)}"]

        sms_results, call_results = notification_service.notify_by_priority(
            priority=severity,
            phone_numbers=recipients,
            message=message,
            sound_url=sound_url,
            voice=voice,
            language=language,
            twilio_service=twilio_service,
        )

        sms_failed = self._count_failed(sms_results)
        sms_sent = len(sms_results) - sms_failed

        actions.append(f"SMS sent: {sms_sent}")
        if sms_failed:
            actions.append(f"SMS failed: {sms_failed}")

        if severity == "LOW":
            actions.append("Low priority: call skipped")
            logger.info("LOW severity alert processed for patient %s (SMS only)", patient_id)
            return actions

        call_failed = self._count_failed(call_results)
        call_sent = len(call_results) - call_failed

        actions.append(f"Calls initiated: {call_sent}")
        if call_failed:
            actions.append(f"Calls failed: {call_failed}")

        logger.warning(
            "Escalated alert processed for patient %s (severity=%s, SMS+CALL)",
            patient_id,
            severity,
        )
        return actions


alert_service = AlertService()
