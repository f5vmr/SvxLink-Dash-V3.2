#!/usr/bin/env python3

import unittest
from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from renderers.svxlink_renderer import (
    render_active_logic,
    render_port_logic,
)


class LogicRenderingTests(unittest.TestCase):

    def capture_single(self, model):
        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer."
            "render_config_template",
            side_effect=capture,
        ):
            result = render_active_logic(model)

        self.assertEqual(result, "rendered")
        return captured

    def test_single_repeater_shared_values(self):
        model = new_node_model()
        model["node"].update({
            "type": "repeater",
            "callsign": "G4NAB",
        })
        model["tones"]["courtesy_mode"] = "beep"
        model["repeater"].update({
            "idle_timeout": 7,
            "sql_timeout": 240,
        })

        captured = self.capture_single(model)
        values = captured["values"]

        self.assertEqual(
            captured["template"],
            "repeater_logic.template",
        )
        self.assertEqual(
            values["RGR_SOUND_ALWAYS"],
            1,
        )
        self.assertEqual(
            values["RGR_SOUND_DELAY"],
            200,
        )
        self.assertEqual(
            values["IDLE_TIMEOUT"],
            7,
        )
        self.assertEqual(
            values["REPEATER_SQL_TIMEOUT"],
            240,
        )

    def test_no_courtesy_uses_zero_delay(self):
        model = new_node_model()
        model["node"].update({
            "type": "simplex",
            "callsign": "G4NAB",
        })
        model["tones"]["courtesy_mode"] = "none"

        captured = self.capture_single(model)
        values = captured["values"]

        self.assertEqual(
            values["RGR_SOUND_ALWAYS"],
            0,
        )
        self.assertEqual(
            values["RGR_SOUND_DELAY"],
            0,
        )

    def test_port_logic_uses_installation_courtesy(self):
        model = new_node_model()
        model["tones"]["courtesy_mode"] = "cw_k"

        node = {
            "role": "simplex",
            "callsign": "G4NAB",
            "ident": {},
            "cw": {},
            "squelch": {
                "method": "gpiod",
                "ctcss_tx": False,
            },
        }

        captured = {}

        def capture(template_name, values):
            captured["template"] = template_name
            captured["values"] = values
            return "rendered"

        with patch(
            "renderers.svxlink_renderer."
            "render_config_template",
            side_effect=capture,
        ):
            result = render_port_logic(
                model,
                "2",
                node,
            )

        self.assertEqual(result, "rendered")
        self.assertEqual(
            captured["values"]["RGR_SOUND_ALWAYS"],
            1,
        )
        self.assertEqual(
            captured["values"]["RGR_SOUND_DELAY"],
            200,
        )
    def test_single_repeater_opening_follows_sql_detector(self):
        for method in (
            "hidraw",
            "gpiod",
            "serial",
        ):
            with self.subTest(method=method):
                model = new_node_model()
                model["node"].update({
                    "type": "repeater",
                    "callsign": "G4NAB",
                })
                model["squelch"].update({
                    "method": method,
                    "ctcss_freq": None,
                })

                values = self.capture_single(
                    model
                )["values"]

                self.assertEqual(
                    values["OPEN_ON_SQL_LINE"],
                    "OPEN_ON_SQL=200",
                )
                self.assertEqual(
                    values["OPEN_ON_CTCSS_LINE"],
                    "#OPEN_ON_CTCSS=200",
                )

    def test_single_repeater_ctcss_uses_ctcss_opening(self):
        model = new_node_model()
        model["node"].update({
            "type": "repeater",
            "callsign": "G4NAB",
        })
        model["squelch"].update({
            "method": "ctcss",
            "ctcss_freq": "88.5",
        })

        values = self.capture_single(
            model
        )["values"]

        self.assertEqual(
            values["OPEN_ON_CTCSS_LINE"],
            "OPEN_ON_CTCSS=200",
        )
        self.assertEqual(
            values["OPEN_ON_SQL_LINE"],
            "#OPEN_ON_SQL=200",
        )

    def test_port_repeater_opening_follows_sql_detector(self):
        model = new_node_model()

        for method, frequency, expected_ctcss, expected_sql in (
            (
                "hidraw",
                None,
                "#OPEN_ON_CTCSS=200",
                "OPEN_ON_SQL=200",
            ),
            (
                "gpiod",
                None,
                "#OPEN_ON_CTCSS=200",
                "OPEN_ON_SQL=200",
            ),
            (
                "serial",
                None,
                "#OPEN_ON_CTCSS=200",
                "OPEN_ON_SQL=200",
            ),
            (
                "ctcss",
                "88.5",
                "OPEN_ON_CTCSS=200",
                "#OPEN_ON_SQL=200",
            ),
        ):
            with self.subTest(method=method):
                node = {
                    "role": "repeater",
                    "callsign": "G4NAB",
                    "ident": {},
                    "cw": {},
                    "repeater": {},
                    "squelch": {
                        "method": method,
                        "ctcss_freq": frequency,
                        "ctcss_tx": False,
                    },
                }
                captured = {}

                def capture(template_name, values):
                    captured["template"] = template_name
                    captured["values"] = values
                    return "rendered"

                with patch(
                    "renderers.svxlink_renderer."
                    "render_config_template",
                    side_effect=capture,
                ):
                    result = render_port_logic(
                        model,
                        "2",
                        node,
                    )

                self.assertEqual(
                    result,
                    "rendered",
                )
                self.assertEqual(
                    captured["template"],
                    "repeater_logic.template",
                )
                self.assertEqual(
                    captured["values"][
                        "OPEN_ON_CTCSS_LINE"
                    ],
                    expected_ctcss,
                )
                self.assertEqual(
                    captured["values"][
                        "OPEN_ON_SQL_LINE"
                    ],
                    expected_sql,
                )
    def test_shared_template_structure(self):
        template_dir = Path(
            "templates/config"
        )

        simplex = (
            template_dir
            / "simplex_logic.template"
        ).read_text(
            encoding="utf-8"
        )

        repeater = (
            template_dir
            / "repeater_logic.template"
        ).read_text(
            encoding="utf-8"
        )

        for template in (
            simplex,
            repeater,
        ):
            self.assertIn(
                "RGR_SOUND_DELAY={{RGR_SOUND_DELAY}}",
                template,
            )
            self.assertIn(
                "RGR_SOUND_ALWAYS={{RGR_SOUND_ALWAYS}}",
                template,
            )
            self.assertIn(
                "MACRO_PREFIX=D",
                template,
            )
            self.assertIn(
                "#QSO_RECORDER=8:QsoRecorder",
                template,
            )
        self.assertIn(
            "#OPEN_ON_1750=800",
            repeater,
        )
        self.assertIn(
            "{{OPEN_ON_CTCSS_LINE}}",
            repeater,
        )
        self.assertIn(
            "{{OPEN_ON_SQL_LINE}}",
            repeater,
        )
        self.assertNotIn(
            "\nOPEN_ON_1750=800",
            repeater,
        )

if __name__ == "__main__":
    unittest.main()
