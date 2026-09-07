#!/usr/bin/env python3

import unittest
from copy import deepcopy

from models.node_model import (
    new_node_model,
    validate_model,
)
from services.model_store import (
    migrate_node_model,
)


class ReflectorOperationalMigrationTests(
    unittest.TestCase
):

    def test_flat_operational_values_are_migrated(self):
        model = new_node_model()

        del model["reflector"]["operational"]

        model["tg_timeout"] = 45
        model["reflector"].update({
            "default_tg": 235,
            "monitor_tgs": [
                235,
                "2350",
                "23560+",
            ],
        })

        self.assertTrue(
            migrate_node_model(model)
        )

        self.assertEqual(
            model["reflector"]["operational"],
            {
                "default_tg": 235,
                "monitor_tgs": [
                    "235",
                    "2350",
                    "23560+",
                ],
                "tg_select_timeout": 45,
            },
        )

        before = deepcopy(model)

        self.assertFalse(
            migrate_node_model(model)
        )

        self.assertEqual(model, before)

    def test_explicit_operational_values_win(self):
        model = new_node_model()

        model["reflector"]["operational"] = {
            "default_tg": 0,
            "monitor_tgs": [],
            "tg_select_timeout": 60,
        }

        model["reflector"].update({
            "default_tg": 235,
            "monitor_tgs": [
                "235",
                "2350",
            ],
        })

        before_operational = deepcopy(
            model["reflector"]["operational"]
        )

        migrate_node_model(model)

        self.assertEqual(
            model["reflector"]["operational"],
            before_operational,
        )


class ReflectorRouteValidationTests(
    unittest.TestCase
):

    def test_federation_uses_nested_fields(self):
        model = new_node_model()

        model["reflector"].update({
            "enabled": True,
            "route": "federation",
        })

        model["reflector"]["federation"].update({
            "network_id": "north_america",
            "name": "North America",
            "host": "north.america.svxlink.net",
            "port": 35300,
            "auth_key": "1234567890ABCDEF",
        })

        errors = validate_model(model)

        self.assertFalse(
            any(
                "Federation" in error
                for error in errors
            ),
            errors,
        )

        model["reflector"]["federation"][
            "auth_key"
        ] = "too-short"

        errors = validate_model(model)

        self.assertIn(
            (
                "Federation subscription password must be "
                "exactly 16 characters."
            ),
            errors,
        )

    def test_protocol_2_requires_name_but_not_fixed_length(
        self
    ):
        model = new_node_model()

        model["reflector"].update({
            "enabled": True,
            "route": "v2",
        })

        model["reflector"]["v2"].update({
            "name": None,
            "host": "v2.example.test",
            "port": 5300,
            "auth_key": "short",
        })

        errors = validate_model(model)

        self.assertIn(
            "Protocol 2 reflector name is required.",
            errors,
        )

        model["reflector"]["v2"]["name"] = (
            "Independent Network"
        )

        errors = validate_model(model)

        self.assertFalse(
            any(
                error.startswith("Protocol 2")
                for error in errors
            ),
            errors,
        )

    def test_protocol_3_uses_nested_certificate_subject(
        self
    ):
        model = new_node_model()

        model["reflector"].update({
            "enabled": True,
            "route": "v3",
        })

        model["reflector"]["v3"].update({
            "name": "Certificate Network",
            "host": "v3.example.test",
            "port": 5300,
        })

        model["reflector"]["v3"]["subject"].update({
            "given_name": "Chris",
            "surname": "Jackson",
            "organizational_unit": "Amateur Radio",
            "organization": "Test Network",
            "locality": "Ashington",
            "state_or_province": "Northumberland",
            "country": "GB",
            "email": "test@example.test",
        })

        errors = validate_model(model)

        self.assertFalse(
            any(
                error.startswith("Protocol 3")
                for error in errors
            ),
            errors,
        )

        model["reflector"]["v3"]["subject"][
            "email"
        ] = ""

        errors = validate_model(model)

        self.assertIn(
            (
                "Protocol 3 certificate email address "
                "is required."
            ),
            errors,
        )


if __name__ == "__main__":
    unittest.main()