import unittest
from copy import deepcopy

from services.topology_ports import get_topology_ports, get_topology_logic_name


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

    def test_invalid_or_ambiguous_configurations_are_rejected(self):
        for model in ({}, {"hardware": {"family": "ics"}},
                      {"node": {"type": "simplex"}, "ports": {"enabled": []}},
                      {"ports": {"enabled": ["1", "1"]}},
                      {"ports": {"enabled": [1]}}):
            with self.subTest(model=model), self.assertRaises(ValueError):
                get_topology_ports(model)


if __name__ == "__main__":
    unittest.main()
