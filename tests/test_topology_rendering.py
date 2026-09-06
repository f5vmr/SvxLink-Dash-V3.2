#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import renderers.svxlink_renderer as renderer


class TopologyRenderingTests(unittest.TestCase):

    def test_reflector_link_uses_selected_ports_only(self):
        model = {
            "hardware": {
                "family": "ics",
            },
            "ports": {
                "enabled": ["1", "2", "3"],
            },
            "installation": {
                "primary_port_id": "2",
            },
            "nodes": {
                "1": {
                    "role": "simplex",
                    "callsign": "PORT1",
                },
                "2": {
                    "role": "repeater",
                    "callsign": "PORT2",
                },
                "3": {
                    "role": "simplex",
                    "callsign": "PORT3",
                },
            },
            "reflector": {
                "enabled": True,
            },
            "topology": {
                "reflector_link": {
                    "name": "LinkToReflector",
                    "ports": ["2", "3"],
                    "default_active": True,
                    "timeout": 300,
                },
                "local_links": [],
                "independent_ports": ["1"],
            },
        }

        captured = {}

        def capture_template(template_name, values):
            captured["template_name"] = template_name
            captured["values"] = values
            return "rendered"

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            result = (
                renderer.render_multiport_link_to_reflector(
                    model
                )
            )

        self.assertEqual(result, "rendered")
        self.assertEqual(
            captured["template_name"],
            "link_to_reflector.template",
        )
        self.assertEqual(
            captured["values"]["CONNECT_LOGICS"],
            (
                "Port2Logic:9,"
                "Port3Logic:9,"
                "ReflectorLogic"
            ),
        )
        self.assertEqual(
            captured["values"]["ACTIVATE_ON_ACTIVITY"],
            "Port2Logic",
        )
        self.assertNotIn(
            "Port1Logic",
            captured["values"]["CONNECT_LOGICS"],
        )

    def test_local_links_render_saved_settings(self):
        model = {
            "hardware": {
                "family": "ics",
            },
            "ports": {
                "enabled": ["1", "2", "3", "4"],
            },
            "nodes": {
                str(port): {
                    "role": "simplex",
                    "callsign": f"PORT{port}",
                }
                for port in range(1, 5)
            },
            "topology": {
                "reflector_link": {
                    "name": "LinkToReflector",
                    "ports": [],
                },
                "local_links": [
                    {
                        "name": "VhfUhfLink",
                        "ports": ["1", "2"],
                        "default_active": True,
                        "timeout": 300,
                    },
                    {
                        "name": "AuxiliaryLink",
                        "ports": ["3", "4"],
                        "default_active": False,
                        "timeout": 120,
                    },
                ],
                "independent_ports": [],
            },
        }

        captured = []

        def capture_template(template_name, values):
            captured.append(
                (template_name, values)
            )
            return f"[{values['LINK_NAME']}]"

        with patch.object(
            renderer,
            "render_config_template",
            side_effect=capture_template,
        ):
            rendered = renderer.render_local_links(model)

        self.assertEqual(
            rendered,
            "[VhfUhfLink]\n\n[AuxiliaryLink]",
        )
        self.assertEqual(len(captured), 2)

        self.assertEqual(
            captured[0],
            (
                "local_link.template",
                {
                    "LINK_NAME": "VhfUhfLink",
                    "CONNECT_LOGICS": (
                        "Port1Logic:9,Port2Logic:9"
                    ),
                    "DEFAULT_ACTIVE": 1,
                    "TIMEOUT": 300,
                },
            ),
        )

        self.assertEqual(
            captured[1],
            (
                "local_link.template",
                {
                    "LINK_NAME": "AuxiliaryLink",
                    "CONNECT_LOGICS": (
                        "Port3Logic:9,Port4Logic:9"
                    ),
                    "DEFAULT_ACTIVE": 0,
                    "TIMEOUT": 120,
                },
            ),
        )

    def test_global_links_follow_topology(self):
        model = {
            "reflector": {
                "enabled": True,
            },
            "topology": {
                "reflector_link": {
                    "name": "LinkToReflector",
                    "ports": ["1"],
                },
                "local_links": [
                    {
                        "name": "VhfUhfLink",
                        "ports": ["2", "3"],
                    },
                ],
                "independent_ports": ["4"],
            },
        }

        self.assertEqual(
            renderer.render_topology_links_line(model),
            "LINKS=LinkToReflector,VhfUhfLink",
        )

        model["reflector"]["enabled"] = False
        model["topology"]["reflector_link"]["ports"] = []

        self.assertEqual(
            renderer.render_topology_links_line(model),
            "LINKS=VhfUhfLink",
        )

        model["topology"]["local_links"] = []

        self.assertEqual(
            renderer.render_topology_links_line(model),
            "#LINKS=",
        )

    def test_renderer_dispatch_uses_model_classification(self):
        ordinary_single = {
            "node": {
                "type": "repeater",
                "callsign": "TEST",
            },
            "hardware": {
                "family": "generic",
            },
            "ports": {
                "enabled": [],
            },
        }

        ics_single = {
            "node": {
                "type": None,
            },
            "hardware": {
                "family": "ics",
            },
            "hardware_profile_id": "ics_1x",
            "ports": {
                "enabled": ["1"],
            },
        }

        dual_usb = {
            "node": {
                "type": None,
            },
            "hardware": {
                "family": "usb_multi_interface",
            },
            "hardware_profile_id": "dual_usb",
            "ports": {
                "enabled": ["1", "2"],
            },
        }

        with patch.object(
            renderer,
            "render_multiport_svxlink_config",
            return_value="MULTIPORT",
        ) as multi_renderer, patch.object(
            renderer,
            "render_active_logic",
            return_value="ACTIVE",
        ), patch.object(
            renderer,
            "render_config_template",
            return_value="SINGLE",
        ):
            self.assertEqual(
                renderer.render_svxlink_config(
                    ordinary_single
                ),
                "SINGLE",
            )
            self.assertEqual(
                renderer.render_svxlink_config(
                    ics_single
                ),
                "MULTIPORT",
            )
            self.assertEqual(
                renderer.render_svxlink_config(
                    dual_usb
                ),
                "MULTIPORT",
            )

        self.assertEqual(
            multi_renderer.call_count,
            2,
        )


if __name__ == "__main__":
    unittest.main()
