import unittest
from copy import deepcopy

from services.topology_ports import (
    get_topology_logic_name,
    get_topology_memberships,
    get_topology_ports,
)

class TopologyPortTests(unittest.TestCase):
    def test_ordinary_roles_have_virtual_identity_without_mutation(self):
        for role, logic in (("simplex", "SimplexLogic"), ("repeater", "RepeaterLogic")):
            with self.subTest(role=role):
                model = {"node": {"type": role}}
                before = deepcopy(model)
                self.assertEqual(get_topology_ports(model), {"1": logic})
                self.assertEqual(get_topology_logic_name(model, "1"), logic)
                self.assertEqual(model, before)

    def test_explicit_single_port_preserves_id(self):
        model = {"node": {"type": "simplex"}, "ports": {"enabled": ["2"]}}
        self.assertEqual(get_topology_ports(model), {"2": "SimplexLogic"})
        with self.assertRaises(ValueError):
            get_topology_logic_name(model, "1")

    def test_ics_one_and_multiple_ports_use_numbered_logics(self):
        for enabled in (["1"], ["2", "1"]):
            model = {"hardware_profile_id": "ics_1x", "ports": {"enabled": enabled}}
            self.assertEqual(list(get_topology_ports(model)), enabled)
            for port in enabled:
                self.assertEqual(get_topology_logic_name(model, port), "Port{}Logic".format(port))

    def test_non_ics_multiple_ports_use_numbered_logics(self):
        model = {
            "ports": {
                "enabled": ["1", "2"],
            },
            "nodes": {
                "1": {
                    "role": "simplex",
                },
                "2": {
                    "role": "repeater",
                },
            },
        }

        self.assertEqual(
            get_topology_ports(model),
            {
                "1": "Port1Logic",
                "2": "Port2Logic",
            },
        )

    def test_topology_memberships_include_every_disposition(self):
        model = {
            "hardware": {
                "family": "ics",
            },
            "ports": {
                "enabled": ["1", "2", "3", "4"],
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
            get_topology_memberships(model),
            {
                "1": ["LinkToReflector"],
                "2": ["VhfUhfLink"],
                "3": ["VhfUhfLink"],
                "4": ["Independent operation"],
            },
        )

    def test_topology_memberships_preserve_conflicts(self):
        model = {
            "hardware": {
                "family": "ics",
            },
            "ports": {
                "enabled": ["1", "2"],
            },
            "topology": {
                "reflector_link": {
                    "name": "LinkToReflector",
                    "ports": ["1", "2"],
                },
                "local_links": [
                    {
                        "name": "LocalRadioLink",
                        "ports": ["2"],
                    },
                ],
                "independent_ports": ["2"],
            },
        }

        before = deepcopy(model)
        memberships = get_topology_memberships(model)

        self.assertEqual(
            memberships["2"],
            [
                "LinkToReflector",
                "LocalRadioLink",
                "Independent operation",
            ],
        )
        self.assertEqual(model, before)

    def test_invalid_or_ambiguous_configurations_are_rejected(self):
        for model in ({}, {"hardware": {"family": "ics"}},
                      {"node": {"type": "simplex"}, "ports": {"enabled": []}},
                      {"ports": {"enabled": ["1", "1"]}},
                      {"ports": {"enabled": [1]}}):
            with self.subTest(model=model), self.assertRaises(ValueError):
                get_topology_ports(model)


if __name__ == "__main__":
    unittest.main()
