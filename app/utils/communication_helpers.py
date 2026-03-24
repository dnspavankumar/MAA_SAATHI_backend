from __future__ import annotations

import re


PHONE_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")
GOOGLE_DRIVE_FILE_PATTERN = re.compile(
    r"^https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
)


def is_valid_phone_number(phone_number: str) -> bool:
    return bool(PHONE_REGEX.match(phone_number.strip()))


def normalize_audio_url(audio_url: str) -> str:
    match = GOOGLE_DRIVE_FILE_PATTERN.match(audio_url.strip())
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return audio_url.strip()


def format_emergency_message(
    patient_name: str,
    emergency_type: str,
    location: str,
) -> str:
    return (
        "EMERGENCY ALERT\n"
        f"Patient: {patient_name}\n"
        f"Type: {emergency_type}\n"
        f"Location: {location}"
    )
