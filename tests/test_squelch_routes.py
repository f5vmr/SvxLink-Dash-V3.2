#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import app as dashboard

from models.node_model import new_node_model


class SquelchRouteTests(unittest.TestCase):

    def test_single_port_saves_commented_com_advanced_example(self):
        model = new_node_model()
        model["platform"]["id"] = "raspberry_pi"

        saved = {}

        def capture_save(saved_model):
            saved["model"] = saved_model

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
            side_effect=capture_save,
        ):
            with dashboard.app.test_request_context(
                "/squelch",
                method="POST",
                data={
                    "squelch_method": "gpiod",
                    "advanced_example": "combine",
                    "combine_components": [
                        "vox",
                        "siglev",
                    ],
                    "manual_detector": "",
                    "sql_gpio_invert": "yes",
                },
            ):
                response = dashboard.squelch_page()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/ident",
        )
        self.assertIs(saved["model"], model)
        self.assertEqual(
            model["squelch"]["method"],
            "gpiod",
        )
        self.assertEqual(
            model["squelch"]["advanced_example"],
            "combine",
        )
        self.assertEqual(
            model["squelch"]["combine_components"],
            [
                "vox",
                "siglev",
            ],
        )
        self.assertIsNone(
            model["squelch"]["manual_detector"]
        )
        self.assertFalse(
            model["squelch"]["ctcss_tx"]
        )

    def test_single_port_invalid_selection_is_not_saved(self):
        model = new_node_model()
        model["platform"]["id"] = "raspberry_pi"

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "render_template",
            return_value="invalid squelch",
        ):
            with dashboard.app.test_request_context(
                "/squelch",
                method="POST",
                data={
                    "squelch_method": "gpiod",
                    "advanced_example": "vox",
                    "manual_detector": "evdev",
                },
            ):
                response = dashboard.squelch_page()

        self.assertEqual(
            response,
            "invalid squelch",
        )
        save_mock.assert_not_called()

    def test_ics_port_saves_specialist_example(self):
        model = new_node_model()
        model["hardware"] = {
            "family": "ics",
        }
        model["hardware_profile_id"] = "ics_1x"
        model["ports"] = {
            "enabled": ["1"],
        }
        model["nodes"] = {
            "1": {
                "role": "simplex",
                "callsign": "TEST",
                "gpio": {},
                "hidraw": {},
                "serial": {},
                "squelch": {
                    "method": "gpiod",
                    "advanced_example": None,
                    "combine_components": [],
                    "manual_detector": None,
                    "ctcss_freq": None,
                    "ctcss_tx": False,
                },
            },
        }

        saved = {}

        def capture_save(saved_model):
            saved["model"] = saved_model

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
            side_effect=capture_save,
        ):
            with dashboard.app.test_request_context(
                "/port-squelch/1",
                method="POST",
                data={
                    "squelch_method": "gpiod",
                    "advanced_example": "",
                    "manual_detector": "pty",
                    "sql_gpio_invert": "no",
                },
            ):
                response = (
                    dashboard.port_squelch_detail_page(
                        "1"
                    )
                )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/port-squelch",
        )
        self.assertIs(saved["model"], model)

        squelch = model["nodes"]["1"]["squelch"]

        self.assertEqual(
            squelch["method"],
            "gpiod",
        )
        self.assertIsNone(
            squelch["advanced_example"]
        )
        self.assertEqual(
            squelch["manual_detector"],
            "pty",
        )
        self.assertTrue(
            model["nodes"]["1"][
                "squelch_configured"
            ]
        )

    def test_ics_port_rejects_unavailable_standard_method(self):
        model = new_node_model()
        model["hardware"] = {
            "family": "ics",
        }
        model["hardware_profile_id"] = "ics_1x"
        model["ports"] = {
            "enabled": ["1"],
        }
        model["nodes"] = {
            "1": {
                "role": "simplex",
                "callsign": "TEST",
                "squelch": {
                    "method": "gpiod",
                    "advanced_example": None,
                    "combine_components": [],
                    "manual_detector": None,
                    "ctcss_freq": None,
                    "ctcss_tx": False,
                },
            },
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "render_template",
            return_value="invalid ICS squelch",
        ):
            with dashboard.app.test_request_context(
                "/port-squelch/1",
                method="POST",
                data={
                    "squelch_method": "hidraw",
                    "advanced_example": "",
                    "manual_detector": "",
                },
            ):
                response = (
                    dashboard.port_squelch_detail_page(
                        "1"
                    )
                )

        self.assertEqual(
            response,
            "invalid ICS squelch",
        )
        save_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
