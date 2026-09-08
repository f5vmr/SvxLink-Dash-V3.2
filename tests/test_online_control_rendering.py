#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from renderers import svxlink_renderer as renderer
from services import model_store as store


EXPECTED_MANUAL_BLOCK = "\n".join([
    "# Emergency DTMF logic control.",
    "# Replace XXXXXX with a private six-digit command.",
    "# Enter XXXXXX0# to take this logic offline.",
    "# Enter XXXXXX1# to return this logic online.",
    "# Prefix the command with * if a module is active.",
    "# DTMF muting prevents the digits being retransmitted.",
    "#ONLINE_CMD=XXXXXX",
    "#ONLINE=1",
])


class OnlineControlRenderingTests(unittest.TestCase):

    def capture_values(self, render_call):
        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture,
        ):
            result = render_call()

        self.assertEqual(result, "rendered")
        return captured

    def test_every_logic_uses_commented_manual_block(self):
        for node_type in (
            "simplex",
            "repeater",
        ):
            with self.subTest(
                scope="single",
                node_type=node_type,
            ):
                model = new_node_model()
                model["node"].update({
                    "type": node_type,
                    "callsign": "G4NAB",
                })

                captured = self.capture_values(
                    lambda: renderer.render_active_logic(
                        model
                    )
                )

                self.assertEqual(
                    captured["values"][
                        "ONLINE_CONTROL_BLOCK"
                    ],
                    EXPECTED_MANUAL_BLOCK,
                )

        for role in (
            "simplex",
            "repeater",
        ):
            with self.subTest(
                scope="port",
                role=role,
            ):
                model = new_node_model()
                node = {
                    "role": role,
                    "callsign": "G4NAB",
                    "ident": {},
                    "cw": {},
                    "repeater": {},
                    "squelch": {
                        "method": "gpiod",
                        "ctcss_tx": False,
                    },
                }

                captured = self.capture_values(
                    lambda: renderer.render_port_logic(
                        model,
                        "2",
                        node,
                    )
                )

                self.assertEqual(
                    captured["values"][
                        "ONLINE_CONTROL_BLOCK"
                    ],
                    EXPECTED_MANUAL_BLOCK,
                )

    def test_save_removes_legacy_online_command(self):
        model = new_node_model()
        model["online_control"] = {
            "enabled": True,
            "command": "345678",
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "node_model.json"

            with patch.object(
                store,
                "CONFIG_DIR",
                root,
            ), patch.object(
                store,
                "MODEL_FILE",
                target,
            ):
                store.save_node_model(model)

            saved = json.loads(
                target.read_text(
                    encoding="utf-8"
                )
            )

        self.assertNotIn(
            "online_control",
            model,
        )
        self.assertNotIn(
            "online_control",
            saved,
        )


if __name__ == "__main__":
    unittest.main()
