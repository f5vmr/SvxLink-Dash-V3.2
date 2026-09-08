#!/usr/bin/env python3

import unittest
from copy import deepcopy
from unittest.mock import patch

import app as dashboard

from models.node_model import new_node_model


class RepeaterRouteTests(unittest.TestCase):

    def test_single_port_accepts_idle_boundaries(self):
        for idle_timeout in (
            "0",
            "10",
        ):
            with self.subTest(
                idle_timeout=idle_timeout
            ):
                model = new_node_model()
                model["node"].update({
                    "type": "repeater",
                    "callsign": "G4NAB",
                })
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
                    with (
                        dashboard.app
                        .test_request_context(
                            "/repeater",
                            method="POST",
                            data={
                                "idle_timeout":
                                    idle_timeout,
                                "sql_timeout": "180",
                            },
                        )
                    ):
                        response = (
                            dashboard.repeater_page()
                        )

                self.assertEqual(
                    response.status_code,
                    302,
                )
                self.assertEqual(
                    response.headers["Location"],
                    "/modules",
                )
                self.assertIs(
                    saved["model"],
                    model,
                )
                self.assertEqual(
                    model["repeater"][
                        "idle_timeout"
                    ],
                    int(idle_timeout),
                )

    def test_single_port_rejects_invalid_timeouts(self):
        invalid_forms = (
            {
                "idle_timeout": "-1",
                "sql_timeout": "180",
            },
            {
                "idle_timeout": "11",
                "sql_timeout": "180",
            },
            {
                "idle_timeout": "10",
                "sql_timeout": "119",
            },
            {
                "idle_timeout": "10",
                "sql_timeout": "301",
            },
            {
                "idle_timeout": "invalid",
                "sql_timeout": "180",
            },
        )

        for form in invalid_forms:
            with self.subTest(form=form):
                model = new_node_model()
                before = deepcopy(model)

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
                    return_value="invalid repeater",
                ):
                    with (
                        dashboard.app
                        .test_request_context(
                            "/repeater",
                            method="POST",
                            data=form,
                        )
                    ):
                        response = (
                            dashboard.repeater_page()
                        )

                self.assertEqual(
                    response,
                    "invalid repeater",
                )
                save_mock.assert_not_called()
                self.assertEqual(
                    model,
                    before,
                )

    def test_multiport_saves_valid_timeouts(self):
        model = new_node_model()
        model["hardware_profile_id"] = "ics_1x"
        model["ports"] = {
            "enabled": ["1"],
        }
        model["nodes"] = {
            "1": {
                "role": "repeater",
                "callsign": "G4NAB",
                "repeater": {
                    "idle_timeout": 10,
                    "sql_timeout": 180,
                    "open_on_sql": 600,
                    "open_sql_flank": "OPEN",
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
            with (
                dashboard.app
                .test_request_context(
                    "/port-repeater",
                    method="POST",
                    data={
                        "port_1_idle_timeout": "0",
                        "port_1_sql_timeout": "300",
                    },
                )
            ):
                response = (
                    dashboard.port_repeater_page()
                )

        self.assertEqual(
            response.status_code,
            302,
        )
        self.assertIs(
            saved["model"],
            model,
        )

        repeater = model["nodes"]["1"]["repeater"]

        self.assertEqual(
            repeater["idle_timeout"],
            0,
        )
        self.assertEqual(
            repeater["sql_timeout"],
            300,
        )
        self.assertNotIn(
            "open_on_sql",
            repeater,
        )
        self.assertNotIn(
            "open_sql_flank",
            repeater,
        )
        self.assertTrue(
            model["nodes"]["1"][
                "repeater_configured"
            ]
        )

    def test_multiport_rejects_invalid_timeouts(self):
        invalid_forms = (
            {
                "port_1_idle_timeout": "-1",
                "port_1_sql_timeout": "180",
            },
            {
                "port_1_idle_timeout": "11",
                "port_1_sql_timeout": "180",
            },
            {
                "port_1_idle_timeout": "10",
                "port_1_sql_timeout": "119",
            },
            {
                "port_1_idle_timeout": "10",
                "port_1_sql_timeout": "301",
            },
            {
                "port_1_idle_timeout": "invalid",
                "port_1_sql_timeout": "180",
            },
        )

        for form in invalid_forms:
            with self.subTest(form=form):
                model = new_node_model()
                model["hardware_profile_id"] = (
                    "ics_1x"
                )
                model["ports"] = {
                    "enabled": ["1"],
                }
                model["nodes"] = {
                    "1": {
                        "role": "repeater",
                        "callsign": "G4NAB",
                        "repeater": {
                            "idle_timeout": 10,
                            "sql_timeout": 180,
                        },
                    },
                }
                before = deepcopy(model)

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
                    return_value="invalid repeater",
                ):
                    with (
                        dashboard.app
                        .test_request_context(
                            "/port-repeater",
                            method="POST",
                            data=form,
                        )
                    ):
                        response = (
                            dashboard
                            .port_repeater_page()
                        )

                self.assertEqual(
                    response,
                    "invalid repeater",
                )
                save_mock.assert_not_called()
                self.assertEqual(
                    model,
                    before,
                )


if __name__ == "__main__":
    unittest.main()
