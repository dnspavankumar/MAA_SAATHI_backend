from typing import Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.utils.communication_helpers import is_valid_phone_number

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class SOSRequest(BaseModel):
    patientId: str = Field(..., min_length=1)
    type: Literal["FALL", "LOW_SPO2", "HIGH_HEART_RATE", "MANUAL_SOS"]
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    location: Location
    doctorNumber: Optional[str] = None
    familyNumbers: list[str] = Field(default_factory=list)
    customMessage: Optional[str] = Field(default=None, min_length=1, max_length=1200)
    soundUrl: Optional[HttpUrl] = None
    voice: str = Field(default="alice", min_length=1, max_length=100)
    language: Optional[str] = Field(default=None, max_length=20)

    @field_validator("doctorNumber")
    @classmethod
    def validate_doctor_number(cls, doctor_number: Optional[str]) -> Optional[str]:
        if doctor_number is None:
            return doctor_number
        if not is_valid_phone_number(doctor_number):
            raise ValueError(f"Invalid doctorNumber: {doctor_number}")
        return doctor_number

    @field_validator("familyNumbers")
    @classmethod
    def validate_family_numbers(cls, family_numbers: list[str]) -> list[str]:
        invalid_numbers = [n for n in family_numbers if not is_valid_phone_number(n)]
        if invalid_numbers:
            invalid = ", ".join(invalid_numbers)
            raise ValueError(f"Invalid familyNumbers: {invalid}")
        return family_numbers

class SOSResponse(BaseModel):
    success: bool
    message: str
    alertId: Optional[str] = None
    actions_taken: Optional[list[str]] = None

class AlertData(BaseModel):
    alertId: str
    patientId: str
    type: str
    severity: str
    status: str
    location: dict
    timestamp: str

class AlertUpdateRequest(BaseModel):
    status: Literal["active", "resolved"]
