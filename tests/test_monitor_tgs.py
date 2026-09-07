#!/usr/bin/env python3

import unittest
from copy import deepcopy
from unittest.mock import patch

import app as dashboard
from models.node_model import new_node_model


class MonitoringTalkGroupTests(unittest.TestCase):

    def setUp(self):
        self.model = new_node_model()

        self.model["node"].update({
            "type": "simplex",
            "callsign": "G4NAB",
        })

        self.model["reflector"].update({
            "enabled": True,
            "route": "v2",
        })

        self.model["reflector"]["v2"].update({
            "name": "Test Network",
            "host": "v2.example.test",
            "port": 5300,
            "auth_key": "password",
        })

    def test_talkgroup_syntax(self):
        valid = {
            "235": "235",
            " 23560+ ": "23560+",
            "23570++": "23570++",
            "000235+": "235+",
            "": "",
        }

        for supplied, expected in valid.items():
            with self.subTest(supplied=supplied):
                self.assertEqual(
                    dashboard.normalise_monitor_talkgroup(
                        supplied
                    ),
                    expected,
                )

        invalid = (
            "0",
            "-235",
            "+235",
            "235+++",
            "235+1",
            "TG235",
        )

        for supplied in invalid:
            with self.subTest(supplied=supplied):
                with self.assertRaises(ValueError):
                    dashboard.normalise_monitor_talkgroup(
                        supplied
                    )

    def test_valid_form_persists_and_rebuilds(self):
        form = {
            "default_tg": "0",
            "tg_select_timeout": "60",
            "enabled_0": "yes",
            "id_0": "235",
            "label_0": "UK",
            "enabled_1": "yes",
            "id_1": "23560+",
            "label_1": "Regional Priority",
            "enabled_2": "yes",
            "id_2": "23570++",
            "label_2": "Highest Priority",
        }

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
            return_value={"success": True},
        ) as build_mock:
            with dashboard.app.test_request_context(
                "/monitor-tgs",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.monitor_tgs_page()
                )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/monitor-tgs?saved=1",
        )

        self.assertEqual(
            self.model["reflector"]["operational"],
            {
                "default_tg": 0,
                "monitor_tgs": [
                    "235",
                    "23560+",
                    "23570++",
                ],
                "tg_select_timeout": 60,
            },
        )

        self.assertEqual(
            self.model["reflector"][
                "monitor_tg_defs"
            ][:3],
            [
                {
                    "id": "235",
                    "label": "UK",
                },
                {
                    "id": "23560+",
                    "label": "Regional Priority",
                },
                {
                    "id": "23570++",
                    "label": "Highest Priority",
                },
            ],
        )

        save_mock.assert_called_once_with(
            self.model
        )
        build_mock.assert_called_once_with(
            self.model,
            restart=True,
        )

    def test_invalid_form_does_not_save_or_build(self):
        original = deepcopy(self.model)

        form = {
            "default_tg": "-1",
            "tg_select_timeout": "0",
            "enabled_0": "yes",
            "id_0": "235",
            "label_0": "First",
            "enabled_1": "yes",
            "id_1": "235++",
            "label_1": "Duplicate",
        }

        captured = {}

        def capture_template(
            template_name,
            **context,
        ):
            captured["template_name"] = (
                template_name
            )
            captured["context"] = context
            return "invalid form"

        with patch.object(
            dashboard,
            "load_node_model",
            return_value=self.model,
        ), patch.object(
            dashboard,
            "save_node_model",
        ) as save_mock, patch.object(
            dashboard,
            "build_svxlink_configuration",
        ) as build_mock, patch.object(
            dashboard,
            "render_template",
            side_effect=capture_template,
        ):
            with dashboard.app.test_request_context(
                "/monitor-tgs",
                method="POST",
                data=form,
            ):
                dashboard.session["authorised"] = True
                response = (
                    dashboard.monitor_tgs_page()
                )

        self.assertEqual(response, "invalid form")
        self.assertEqual(
            captured["template_name"],
            "monitor_tgs.html",
        )

        error = captured["context"]["error"]

        self.assertIn(
            "Default TalkGroup must be 0",
            error,
        )
        self.assertIn(
            "selection timeout must be a positive",
            error,
        )
        self.assertIn(
            "TalkGroup 235 is entered more than once.",
            error,
        )

        save_mock.assert_not_called()
        build_mock.assert_not_called()
        self.assertEqual(self.model, original)


if __name__ == "__main__":
    unittest.main()