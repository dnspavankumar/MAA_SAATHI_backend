from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

from app.utils.communication_helpers import is_valid_phone_number


class TwilioActionResult(BaseModel):
    phone_number: str
    status: str
    sid: str | None = None
    error: str | None = None


class SMSRequest(BaseModel):
    phone_numbers: list[str] = Field(min_length=1)
    message: str = Field(min_length=1, max_length=1200)

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, phone_numbers: list[str]) -> list[str]:
        invalid_numbers = [n for n in phone_numbers if not is_valid_phone_number(n)]
        if invalid_numbers:
            invalid = ", ".join(invalid_numbers)
            raise ValueError(f"Invalid phone number(s): {invalid}")
        return phone_numbers


class CallRequest(BaseModel):
    phone_numbers: list[str] = Field(min_length=1)
    message: str = Field(min_length=1, max_length=1200)
    sound_url: HttpUrl | None = None
    voice: str = Field(default="alice", min_length=1, max_length=100)
    language: str | None = Field(default=None, max_length=20)

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, phone_numbers: list[str]) -> list[str]:
        invalid_numbers = [n for n in phone_numbers if not is_valid_phone_number(n)]
        if invalid_numbers:
            invalid = ", ".join(invalid_numbers)
            raise ValueError(f"Invalid phone number(s): {invalid}")
        return phone_numbers


class CommunicationSOSRequest(BaseModel):
    patient_name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=500)
    emergency_type: str = Field(min_length=1, max_length=100)
    priority: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
    doctor_number: str | None = None
    family_numbers: list[str] = Field(default_factory=list)
    sound_url: HttpUrl | None = None
    voice: str = Field(default="alice", min_length=1, max_length=100)
    language: str | None = Field(default=None, max_length=20)

    @field_validator("doctor_number")
    @classmethod
    def validate_doctor_number(cls, doctor_number: str | None) -> str | None:
        if doctor_number is None:
            return doctor_number
        if not is_valid_phone_number(doctor_number):
            raise ValueError(f"Invalid doctor_number: {doctor_number}")
        return doctor_number

    @field_validator("family_numbers")
    @classmethod
    def validate_family_numbers(cls, family_numbers: list[str]) -> list[str]:
        invalid_numbers = [n for n in family_numbers if not is_valid_phone_number(n)]
        if invalid_numbers:
            invalid = ", ".join(invalid_numbers)
            raise ValueError(f"Invalid family number(s): {invalid}")
        return family_numbers

    @model_validator(mode="after")
    def validate_contact_numbers(self) -> "CommunicationSOSRequest":
        if self.doctor_number is None and not self.family_numbers:
            raise ValueError("At least one contact number is required")
        return self


class BatchResponse(BaseModel):
    success: bool
    route: Literal["sms", "call"]
    total: int
    sent: int
    failed: int
    results: list[TwilioActionResult]


class CommunicationSOSResponse(BaseModel):
    success: bool
    route: Literal["sos"] = "sos"
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    total_contacts: int
    sms_sent: int
    call_sent: int
    failed: int
    sms_results: list[TwilioActionResult]
    call_results: list[TwilioActionResult]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
