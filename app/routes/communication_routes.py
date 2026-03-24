from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.communication_schema import (
    BatchResponse,
    CallRequest,
    CommunicationSOSRequest,
    CommunicationSOSResponse,
    SMSRequest,
    TwilioActionResult,
)
from app.services.notification_service import notification_service
from app.services.twilio_service import TwilioService, get_twilio_service
from app.utils.communication_helpers import format_emergency_message
from app.utils.logger import logger


router = APIRouter(prefix="/api/v1/communication", tags=["Communication"])


def _count_failed(results: list[TwilioActionResult]) -> int:
    return sum(1 for result in results if result.status == "failed")


@router.post("/sms", response_model=BatchResponse)
def send_sms(
    payload: SMSRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
) -> BatchResponse:
    try:
        results = notification_service.send_sms_batch(
            phone_numbers=payload.phone_numbers,
            message=payload.message,
            twilio_service=twilio_service,
        )
    except RuntimeError as exc:
        logger.exception("SMS route runtime error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    failed = _count_failed(results)
    sent = len(results) - failed
    return BatchResponse(
        success=failed == 0,
        route="sms",
        total=len(results),
        sent=sent,
        failed=failed,
        results=results,
    )


@router.post("/call", response_model=BatchResponse)
def make_calls(
    payload: CallRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
) -> BatchResponse:
    try:
        results = notification_service.make_call_batch(
            phone_numbers=payload.phone_numbers,
            message=payload.message,
            sound_url=str(payload.sound_url) if payload.sound_url else None,
            voice=payload.voice,
            language=payload.language,
            twilio_service=twilio_service,
        )
    except RuntimeError as exc:
        logger.exception("Call route runtime error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    failed = _count_failed(results)
    sent = len(results) - failed
    return BatchResponse(
        success=failed == 0,
        route="call",
        total=len(results),
        sent=sent,
        failed=failed,
        results=results,
    )


@router.post("/sos", response_model=CommunicationSOSResponse)
def send_sos(
    payload: CommunicationSOSRequest,
    twilio_service: TwilioService = Depends(get_twilio_service),
) -> CommunicationSOSResponse:
    message = format_emergency_message(
        patient_name=payload.patient_name,
        emergency_type=payload.emergency_type,
        location=payload.location,
    )
    recipients = []
    if payload.doctor_number:
        recipients.append(payload.doctor_number)
    recipients.extend(payload.family_numbers)

    try:
        sms_results, call_results = notification_service.notify_by_priority(
            priority=payload.priority,
            phone_numbers=recipients,
            message=message,
            sound_url=str(payload.sound_url) if payload.sound_url else None,
            voice=payload.voice,
            language=payload.language,
            twilio_service=twilio_service,
        )
    except RuntimeError as exc:
        logger.exception("SOS route runtime error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    sms_failed = _count_failed(sms_results)
    call_failed = _count_failed(call_results)
    failed = sms_failed + call_failed

    return CommunicationSOSResponse(
        success=failed == 0,
        priority=payload.priority,
        total_contacts=len(notification_service.unique_recipients(recipients)),
        sms_sent=len(sms_results) - sms_failed,
        call_sent=len(call_results) - call_failed,
        failed=failed,
        sms_results=sms_results,
        call_results=call_results,
    )
