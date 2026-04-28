from __future__ import annotations

import json
from pathlib import Path


class SchemaValidationError(ValueError):
    pass


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_payload(payload: object, schema: dict, path: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type is not None:
        _validate_type(payload, expected_type, path)

    if expected_type == "object":
        if not isinstance(payload, dict):
            raise SchemaValidationError(f"{path} must be an object")
        required = schema.get("required", [])
        for key in required:
            if key not in payload:
                raise SchemaValidationError(f"{path}.{key} is required")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in payload:
                validate_payload(payload[key], subschema, f"{path}.{key}")

    if expected_type == "array":
        if not isinstance(payload, list):
            raise SchemaValidationError(f"{path} must be an array")


def validate_payload_from_schema_file(payload: object, schema_path: str | Path) -> None:
    validate_payload(payload, load_schema(schema_path))


def _validate_type(payload: object, expected_type: str, path: str) -> None:
    type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "number": (int, float),
        "boolean": bool,
        "null": type(None),
    }
    python_type = type_map.get(expected_type)
    if python_type is None:
        raise SchemaValidationError(f"{path} uses unsupported schema type '{expected_type}'")
    if not isinstance(payload, python_type):
        raise SchemaValidationError(f"{path} must be of type {expected_type}")
