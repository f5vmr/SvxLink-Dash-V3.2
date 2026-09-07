#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from models.node_model import new_node_model
import renderers.svxlink_renderer as renderer


class ReflectorRenderingTests(unittest.TestCase):

    def setUp(self):
        self.model = new_node_model()

        self.model["node"].update({
            "type": "simplex",
            "callsign": "G4NAB",
            "language": "en_GB",
        })

        self.model["reflector"]["enabled"] = True

        self.model["reflector"]["operational"].update({
            "default_tg": 235,
            "monitor_tgs": [
                "235",
                "2350",
                "23560+",
            ],
            "tg_select_timeout": 60,
        })

    def capture_render(self):
        captured = {}

        def capture_template(template_name, values):
            captured["template_name"] = (
                template_name
            )
            captured["values"] = values
            return "rendered"

        return captured, capture_template

    def test_federation_uses_federation_settings(self):
        self.model["reflector"]["route"] = (
            "federation"
        )

        self.model["reflector"]["federation"].update({
            "network_id": "north_america",
            "name": "North America",
            "host": "north.america.svxlink.net",
            "port": 35300,
            "auth_key": "1234567890ABCDEF",
        })

        captured, capture_template = (
            self.capture_render()
        )

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            result = renderer.render_reflector_logic(
                self.model
            )

        self.assertEqual(result, "rendered")
        self.assertEqual(
            captured["template_name"],
            "reflector_logic.template",
        )

        values = captured["values"]

        self.assertEqual(
            values["REFLECTOR_HOST"],
            "north.america.svxlink.net",
        )
        self.assertEqual(
            values["REFLECTOR_PORT"],
            35300,
        )
        self.assertEqual(
            values["REFLECTOR_AUTH_KEY"],
            "1234567890ABCDEF",
        )
        self.assertEqual(
            values["CALLSIGN"],
            "G4NAB",
        )
        self.assertEqual(
            values["DEFAULT_TG"],
            235,
        )
        self.assertEqual(
            values["MONITOR_TGS"],
            "235,2350,23560+",
        )
        self.assertEqual(
            values["TG_SELECT_TIMEOUT"],
            60,
        )
        self.assertEqual(
            values["TG_SELECT_INHIBIT_TIMEOUT"],
            60,
        )

    def test_protocol_2_does_not_use_federation_settings(
        self
    ):
        self.model["reflector"]["route"] = "v2"

        self.model["reflector"]["federation"].update({
            "host": "federation.example.test",
            "port": 35300,
            "auth_key": "1234567890ABCDEF",
        })

        self.model["reflector"]["v2"].update({
            "name": "Independent Network",
            "host": "v2.example.test",
            "port": 5300,
            "auth_key": "short-password",
        })

        captured, capture_template = (
            self.capture_render()
        )

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            renderer.render_reflector_logic(
                self.model
            )

        values = captured["values"]

        self.assertEqual(
            captured["template_name"],
            "reflector_logic.template",
        )
        self.assertEqual(
            values["REFLECTOR_HOST"],
            "v2.example.test",
        )
        self.assertEqual(
            values["REFLECTOR_PORT"],
            5300,
        )
        self.assertEqual(
            values["REFLECTOR_AUTH_KEY"],
            "short-password",
        )

    def test_protocol_3_uses_certificate_template(self):
        self.model["reflector"]["route"] = "v3"

        self.model["reflector"]["v3"].update({
            "name": "Certificate Network",
            "host": "v3.example.test",
            "port": 5300,
        })

        self.model["reflector"]["v3"]["subject"].update({
            "given_name": "Chris",
            "surname": "Jackson",
            "organizational_unit": "Amateur Radio",
            "organization": "Test Network",
            "locality": "Ashington",
            "state_or_province": "Northumberland",
            "country": "GB",
            "email": "test@example.test",
        })

        captured, capture_template = (
            self.capture_render()
        )

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            renderer.render_reflector_logic(
                self.model
            )

        values = captured["values"]

        self.assertEqual(
            captured["template_name"],
            "reflector_logic_v3.template",
        )
        self.assertEqual(
            values["REFLECTOR_HOST"],
            "v3.example.test",
        )
        self.assertEqual(
            values["CALLSIGN"],
            "G4NAB",
        )
        self.assertNotIn(
            "REFLECTOR_AUTH_KEY",
            values,
        )
        self.assertEqual(
            values["CERT_GIVEN_NAME"],
            "Chris",
        )
        self.assertEqual(
            values["CERT_SURNAME"],
            "Jackson",
        )
        self.assertEqual(
            values["CERT_COUNTRY"],
            "GB",
        )
        self.assertEqual(
            values["CERT_EMAIL"],
            "test@example.test",
        )

    def test_legacy_v2_fallback_and_primary_callsign(
        self
    ):
        self.model["reflector"]["route"] = None
        self.model["reflector"].update({
            "host": "legacy.example.test",
            "port": 5300,
            "auth_key": "legacy-password",
        })

        self.model["hardware"] = {
            "family": "ics",
        }
        self.model["ports"] = {
            "enabled": ["1", "2"],
        }
        self.model["installation"] = {
            "primary_port_id": "2",
        }
        self.model["nodes"] = {
            "1": {
                "callsign": "SECONDARY",
                "role": "simplex",
            },
            "2": {
                "callsign": "PRIMARY",
                "role": "repeater",
            },
        }

        captured, capture_template = (
            self.capture_render()
        )

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            renderer.render_reflector_logic(
                self.model
            )

        values = captured["values"]

        self.assertEqual(
            captured["template_name"],
            "reflector_logic.template",
        )
        self.assertEqual(
            values["REFLECTOR_HOST"],
            "legacy.example.test",
        )
        self.assertEqual(
            values["REFLECTOR_AUTH_KEY"],
            "legacy-password",
        )
        self.assertEqual(
            values["CALLSIGN"],
            "PRIMARY",
        )


if __name__ == "__main__":
    unittest.main()
    