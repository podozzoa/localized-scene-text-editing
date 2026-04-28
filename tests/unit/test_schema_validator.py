from __future__ import annotations

import unittest

from harness.schemas.validator import SchemaValidationError, validate_payload


class SchemaValidatorUnitTest(unittest.TestCase):
    def test_validate_payload_accepts_valid_object(self) -> None:
        schema = {
            "type": "object",
            "required": ["name", "items"],
            "properties": {
                "name": {"type": "string"},
                "items": {"type": "array"},
            },
        }
        payload = {"name": "run", "items": []}

        validate_payload(payload, schema)

    def test_validate_payload_rejects_missing_required_key(self) -> None:
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }

        with self.assertRaises(SchemaValidationError):
            validate_payload({}, schema)

    def test_validate_payload_rejects_wrong_type(self) -> None:
        schema = {"type": "array"}

        with self.assertRaises(SchemaValidationError):
            validate_payload({}, schema)


if __name__ == "__main__":
    unittest.main()
