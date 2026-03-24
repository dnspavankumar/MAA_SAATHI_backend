from __future__ import annotations

from functools import lru_cache
from xml.sax.saxutils import escape

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.config.settings import settings
from app.schemas.communication_schema import TwilioActionResult
from app.utils.communication_helpers import normalize_audio_url
from app.utils.logger import logger


class TwilioService:
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(self, to: str, message: str) -> TwilioActionResult:
        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to,
            )
            return TwilioActionResult(
                phone_number=to,
                status=str(msg.status),
                sid=msg.sid,
            )
        except TwilioRestException as exc:
            logger.exception("Twilio SMS error for %s", to)
            return TwilioActionResult(
                phone_number=to,
                status="failed",
                error=str(exc.msg or exc),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected SMS error for %s", to)
            return TwilioActionResult(
                phone_number=to,
                status="failed",
                error=str(exc),
            )

    def make_call(
        self,
        to: str,
        message: str,
        sound_url: str | None = None,
        voice: str = "alice",
        language: str | None = None,
    ) -> TwilioActionResult:
        try:
            twiml_parts = ["<Response>"]
            if sound_url:
                normalized_url = normalize_audio_url(sound_url)
                twiml_parts.append(f"<Play>{escape(normalized_url)}</Play>")
            say_attributes: list[str] = [f' voice="{escape(voice)}"']
            if language:
                say_attributes.append(f' language="{escape(language)}"')
            twiml_parts.append(
                f"<Say{''.join(say_attributes)}>{escape(message)}</Say>",
            )
            twiml_parts.append("</Response>")
            twiml_message = "".join(twiml_parts)
            call = self.client.calls.create(
                twiml=twiml_message,
                from_=self.from_number,
                to=to,
            )
            return TwilioActionResult(
                phone_number=to,
                status=str(call.status),
                sid=call.sid,
            )
        except TwilioRestException as exc:
            logger.exception("Twilio call error for %s", to)
            return TwilioActionResult(
                phone_number=to,
                status="failed",
                error=str(exc.msg or exc),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected call error for %s", to)
            return TwilioActionResult(
                phone_number=to,
                status="failed",
                error=str(exc),
            )


def _require_twilio_settings() -> tuple[str, str, str]:
    account_sid = (settings.twilio_account_sid or "").strip()
    auth_token = (settings.twilio_auth_token or "").strip()
    phone_number = (settings.twilio_phone_number or "").strip()

    missing_vars = []
    if not account_sid:
        missing_vars.append("TWILIO_ACCOUNT_SID")
    if not auth_token:
        missing_vars.append("TWILIO_AUTH_TOKEN")
    if not phone_number:
        missing_vars.append("TWILIO_PHONE_NUMBER")

    if missing_vars:
        missing = ", ".join(missing_vars)
        raise RuntimeError(f"Missing required environment variables: {missing}")

    return account_sid, auth_token, phone_number


@lru_cache(maxsize=1)
def get_twilio_service() -> TwilioService:
    account_sid, auth_token, phone_number = _require_twilio_settings()
    return TwilioService(
        account_sid=account_sid,
        auth_token=auth_token,
        from_number=phone_number,
    )
