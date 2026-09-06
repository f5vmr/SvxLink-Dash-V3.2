"""Regression checks using in-memory models and temporary storage only."""

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from models.node_model import new_node_model
from services import model_store as store


class TopologyMigrationTests(unittest.TestCase):
    def setUp(self):
        self.model = new_node_model()
        self.model["ports"] = {"available": [1, 2, 3, 4], "enabled": [3, 1]}
        self.model["installation"]["primary_port_id"] = 3
        self.model["nodes"] = {"2": {"callsign": "KEEP", "audio": {"rx_channel": 0}}}
        self.model["reflector"]["v2"]["port"] = 5300
        self.topology = self.model["topology"]
        self.topology["reflector_link"].update(ports=[1, 2], timeout=123)
        self.topology["local_links"] = [
            {"name": "Local", "ports": [3, 4], "timeout": 99},
            {"name": "Empty", "ports": [2, 4]},
        ]
        self.topology["independent_ports"] = [4, 3, 3]

    def test_normalisation_preserves_order_membership_and_numeric_settings(self):
        self.assertTrue(store.normalise_port_ids(self.model))
        self.assertEqual(self.model["ports"], {
            "available": ["1", "2", "3", "4"], "enabled": ["3", "1"],
        })
        self.assertEqual(self.model["installation"]["primary_port_id"], "3")
        self.assertEqual(self.topology["reflector_link"]["ports"], ["1", "2"])
        self.assertEqual(self.topology["local_links"][0]["ports"], ["3", "4"])
        self.assertEqual(self.topology["independent_ports"], ["4", "3", "3"])
        self.assertEqual(self.model["reflector"]["v2"]["port"], 5300)
        self.assertEqual(self.model["nodes"]["2"]["audio"]["rx_channel"], 0)
        self.assertFalse(store.normalise_port_ids(self.model))

    def test_migration_preserves_link_settings_and_disabled_node_data(self):
        self.assertTrue(store.migrate_node_model(self.model))
        self.assertEqual(self.topology["reflector_link"]["ports"], ["1"])
        self.assertEqual(self.topology["reflector_link"]["timeout"], 123)
        self.assertEqual(self.topology["local_links"], [
            {"name": "Local", "ports": ["3"], "timeout": 99},
            {"name": "Empty", "ports": []},
        ])
        self.assertEqual(self.topology["independent_ports"], ["3", "3"])
        self.assertEqual(self.model["nodes"]["2"]["callsign"], "KEEP")
        before = deepcopy(self.model)
        self.assertFalse(store.migrate_node_model(self.model))
        self.assertEqual(self.model, before)

    def test_empty_selection_removes_memberships(self):
        self.model["ports"]["enabled"] = []
        self.assertTrue(store.clean_stale_topology_ports(self.model))
        self.assertEqual(self.topology["reflector_link"]["ports"], [])
        self.assertEqual(self.topology["independent_ports"], [])
        self.assertTrue(all(not link["ports"] for link in self.topology["local_links"]))
        self.assertFalse(store.clean_stale_topology_ports(self.model))

    def test_absent_or_malformed_selection_does_not_erase_memberships(self):
        for ports in (None, {}, {"enabled": None}):
            with self.subTest(ports=ports):
                self.model["ports"] = ports
                before = deepcopy(self.model)
                self.assertFalse(store.clean_stale_topology_ports(self.model))
                self.assertEqual(self.model, before)

    def test_legacy_migration_is_idempotent_with_and_without_reflector(self):
        for enabled in (False, True):
            with self.subTest(reflector_enabled=enabled):
                model = {"ports": {"enabled": [1, 2]},
                         "reflector": {"enabled": enabled}}
                self.assertTrue(store.migrate_node_model(model))
                self.assertEqual(model["installation"]["primary_port_id"], "1")
                topology = model["topology"]
                self.assertEqual(topology["reflector_link"]["ports"],
                                 ["1", "2"] if enabled else [])
                self.assertEqual(topology["independent_ports"],
                                 [] if enabled else ["1", "2"])
                before = deepcopy(model)
                self.assertFalse(store.migrate_node_model(model))
                self.assertEqual(model, before)

    def test_defaults_merge_preserves_operator_values(self):
        del self.topology["reflector_link"]["default_active"]
        self.assertTrue(store.migrate_node_model(self.model))
        self.assertTrue(self.topology["reflector_link"]["default_active"])
        self.assertEqual(self.topology["reflector_link"]["timeout"], 123)
        self.assertFalse(store.migrate_node_model(self.model))
        self.assertFalse(store.migrate_node_model(new_node_model()))

    def test_partially_migrated_legacy_model_preserves_explicit_choices(self):
        for version in (None, 1, "1"):
            with self.subTest(version=version):
                model = {
                    "ports": {"enabled": ["1", "2", "3"]},
                    "installation": {"primary_port_id": "2"},
                    "build": {"tones_configured": False},
                    "courtesy": {"mode": "beep", "frequency": 900},
                    "tones": {"courtesy_mode": "none", "courtesy_frequency": 0,
                              "custom": "keep"},
                    "reflector": {
                        "enabled": True, "route": "v3", "host": "legacy.example",
                        "auth_key": "legacy", "default_tg": 123,
                        "v2": {"host": "saved.example", "auth_key": "saved",
                               "default_tg": 0, "monitor_tgs": []},
                        "v3": {"host": "certificate.example", "subject": {"email": "a@example.org"}},
                    },
                    "topology": {
                        "reflector_link": {"ports": ["2"], "default_active": False, "timeout": 0},
                        "local_links": [{"name": "Local", "ports": ["1", "3"]}],
                        "independent_ports": [],
                    },
                    "node_info": {"lat": "-34.5", "long": "-58.4"},
                    "location_info": {"enabled": False, "tx_offset_khz": -600},
                    "custom": {"operator_value": [1, False, "keep"]},
                }
                if version is not None:
                    model["schema_version"] = version
                before = deepcopy(model)
                self.assertTrue(store.migrate_node_model(model))

                def assert_preserved(original, migrated):
                    for key, value in original.items():
                        if key == "schema_version":
                            continue
                        if isinstance(value, dict):
                            assert_preserved(value, migrated[key])
                        else:
                            self.assertEqual(migrated[key], value, key)

                assert_preserved(before, model)
                self.assertEqual(model["schema_version"], 2)
                self.assertIn("idle_mode", model["tones"])
                self.assertEqual(model["topology"]["reflector_link"]["name"], "LinkToReflector")
                snapshot = deepcopy(model)
                self.assertFalse(store.migrate_node_model(model))
                self.assertEqual(model, snapshot)

    def test_existing_partial_topology_does_not_infer_memberships(self):
        model = {"ports": {"enabled": [1, 2]},
                 "reflector": {"enabled": True},
                 "topology": {"independent_ports": [2]}}
        self.assertTrue(store.migrate_node_model(model))
        self.assertEqual(model["topology"]["reflector_link"]["ports"], [])
        self.assertEqual(model["topology"]["independent_ports"], ["2"])

    def test_save_cleans_memberships_and_repeated_save_is_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "node_model.json"
            with patch.object(store, "CONFIG_DIR", root), patch.object(store, "MODEL_FILE", target):
                store.save_node_model(self.model)
                first = target.read_bytes()
                saved = json.loads(first)
                self.assertEqual(saved["topology"]["reflector_link"]["ports"], ["1"])
                self.assertEqual(saved["topology"]["local_links"][0]["ports"], ["3"])
                store.save_node_model(self.model)
                self.assertEqual(target.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
