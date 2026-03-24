from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


class FirebaseSchemaValidationError(ValueError):
    """Raised when a Firestore document does not match the shared schema."""


_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "shared" / "firebase.common.schema.json"
_SCHEMA_CACHE: dict[str, Any] | None = None


def load_firebase_schema() -> dict[str, Any]:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        with _SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
            _SCHEMA_CACHE = json.load(schema_file)
    return _SCHEMA_CACHE


def get_collection_schema(schema_key: str) -> dict[str, Any]:
    schema = load_firebase_schema()
    collections = schema.get("collections", {})
    entry = collections.get(schema_key)
    if entry is None:
        raise FirebaseSchemaValidationError(f'Unknown schema key: "{schema_key}"')
    return entry


def validate_firestore_document(schema_key: str, data: dict[str, Any], *, partial: bool = False) -> bool:
    if not isinstance(data, dict):
        raise FirebaseSchemaValidationError(f'"{schema_key}" data must be a dictionary')

    entry = get_collection_schema(schema_key)
    required = entry.get("required", [])
    fields = entry.get("fields", {})
    enums = entry.get("enums", {})
    allow_additional = entry.get("allowAdditionalFields", True)

    if not partial:
        missing = [field for field in required if data.get(field) is None]
        if missing:
            raise FirebaseSchemaValidationError(
                f'"{schema_key}" missing required fields: {", ".join(missing)}'
            )

    for field, value in data.items():
        if value is None:
            continue

        expected_type = fields.get(field)
        if expected_type is None:
            if not allow_additional:
                raise FirebaseSchemaValidationError(f'"{schema_key}" unexpected field: {field}')
            continue

        if not _matches_type(expected_type, value):
            raise FirebaseSchemaValidationError(f'"{schema_key}.{field}" must be {expected_type}')

        allowed_values = enums.get(field)
        if isinstance(allowed_values, list) and value not in allowed_values:
            allowed_text = ", ".join(str(item) for item in allowed_values)
            raise FirebaseSchemaValidationError(
                f'"{schema_key}.{field}" must be one of: {allowed_text}'
            )

    return True


def _matches_type(expected_type: str, value: Any) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "string[]":
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if expected_type == "date":
        return isinstance(value, date) or _is_iso_date_string(value)
    if expected_type == "timestamp":
        return isinstance(value, (datetime, date, int, float, str))
    if expected_type == "latlng":
        return _is_latlng(value)
    return True


def _is_iso_date_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _is_latlng(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    lat = value.get("lat")
    lng = value.get("lng")
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return False
    if lat < -90 or lat > 90:
        return False
    if lng < -180 or lng > 180:
        return False
    return True
