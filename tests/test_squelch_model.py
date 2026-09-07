#!/usr/bin/env python3

import unittest

from models.node_model import (
    ADVANCED_SQUELCH_METHODS,
    MANUAL_SQUELCH_DETECTORS,
    STANDARD_SQUELCH_METHODS,
    SUPPORTED_SQUELCH_METHODS,
    new_node_model,
    squelch_uses_ctcss,
    validate_model,
    validate_squelch_configuration,
)


class SquelchModelTests(unittest.TestCase):

    def test_detector_categories_are_distinct(self):
        standard = set(STANDARD_SQUELCH_METHODS)
        advanced = set(ADVANCED_SQUELCH_METHODS)
        manual = set(MANUAL_SQUELCH_DETECTORS)

        self.assertFalse(standard & advanced)
        self.assertFalse(standard & manual)
        self.assertFalse(advanced & manual)

    def test_active_methods_are_standard_only(self):
        self.assertEqual(
            set(SUPPORTED_SQUELCH_METHODS),
            {
                "hidraw",
                "gpiod",
                "serial",
                "ctcss",
            },
        )

    def test_advanced_and_specialist_choices(self):
        self.assertEqual(
            set(ADVANCED_SQUELCH_METHODS),
            {
                "vox",
                "siglev",
                "combine",
            },
        )
        self.assertEqual(
            set(MANUAL_SQUELCH_DETECTORS),
            {
                "evdev",
                "pty",
                "rtl_sdr",
            },
        )

    def test_new_model_has_safe_defaults(self):
        squelch = new_node_model()["squelch"]

        self.assertEqual(
            squelch["method"],
            "hidraw",
        )
        self.assertIsNone(
            squelch["advanced_example"]
        )
        self.assertEqual(
            squelch["combine_components"],
            [],
        )
        self.assertIsNone(
            squelch["manual_detector"]
        )
        self.assertIsNone(
            squelch["ctcss_freq"]
        )
        self.assertFalse(
            squelch["ctcss_tx"]
        )


class SquelchValidationTests(unittest.TestCase):

    def errors(self, squelch):
        return validate_squelch_configuration(
            squelch,
            "Port 2 squelch",
        )

    def valid_squelch(self):
        return {
            "method": "gpiod",
            "advanced_example": None,
            "combine_components": [],
            "manual_detector": None,
            "ctcss_freq": None,
            "ctcss_tx": False,
        }

    def test_standard_detectors_are_valid(self):
        for method in STANDARD_SQUELCH_METHODS:
            with self.subTest(method=method):
                squelch = self.valid_squelch()
                squelch["method"] = method

                if method == "ctcss":
                    squelch["ctcss_freq"] = "88.5"

                self.assertEqual(
                    self.errors(squelch),
                    [],
                )

    def test_advanced_examples_keep_standard_active(self):
        for advanced_example in (
            "vox",
            "siglev",
        ):
            with self.subTest(
                advanced_example=advanced_example
            ):
                squelch = self.valid_squelch()
                squelch["advanced_example"] = (
                    advanced_example
                )

                self.assertEqual(
                    self.errors(squelch),
                    [],
                )

    def test_valid_combine_example(self):
        squelch = self.valid_squelch()
        squelch.update({
            "advanced_example": "combine",
            "combine_components": [
                "ctcss",
                "siglev",
                "vox",
            ],
            "ctcss_freq": "88.5",
        })

        self.assertEqual(
            self.errors(squelch),
            [],
        )
        self.assertTrue(
            squelch_uses_ctcss(squelch)
        )

    def test_combine_requires_two_or_three_components(self):
        cases = (
            [],
            ["vox"],
            [
                "vox",
                "siglev",
                "ctcss",
                "vox",
            ],
        )

        for components in cases:
            with self.subTest(
                components=components
            ):
                squelch = self.valid_squelch()
                squelch.update({
                    "advanced_example": "combine",
                    "combine_components": components,
                })

                self.assertTrue(
                    self.errors(squelch)
                )

    def test_combine_rejects_duplicate_and_unknown_types(self):
        squelch = self.valid_squelch()
        squelch.update({
            "advanced_example": "combine",
            "combine_components": [
                "vox",
                "vox",
            ],
        })

        self.assertIn(
            "same detector component",
            " ".join(self.errors(squelch)),
        )

        squelch["combine_components"] = [
            "vox",
            "gpiod",
        ]

        self.assertIn(
            "unsupported detector component",
            " ".join(self.errors(squelch)),
        )

    def test_specialist_examples_are_valid(self):
        for detector in MANUAL_SQUELCH_DETECTORS:
            with self.subTest(detector=detector):
                squelch = self.valid_squelch()
                squelch["manual_detector"] = (
                    detector
                )

                self.assertEqual(
                    self.errors(squelch),
                    [],
                )

    def test_invalid_specialist_is_rejected(self):
        squelch = self.valid_squelch()
        squelch["manual_detector"] = (
            "legacy_gpio"
        )

        self.assertIn(
            "specialist example must be",
            " ".join(self.errors(squelch)),
        )

    def test_advanced_and_specialist_are_exclusive(self):
        squelch = self.valid_squelch()
        squelch.update({
            "advanced_example": "vox",
            "manual_detector": "evdev",
        })

        self.assertIn(
            "cannot select both",
            " ".join(self.errors(squelch)),
        )

    def test_stale_combine_components_are_rejected(self):
        squelch = self.valid_squelch()
        squelch["combine_components"] = [
            "vox",
            "siglev",
        ]

        self.assertIn(
            "cannot retain COMBINE components",
            " ".join(self.errors(squelch)),
        )

    def test_ctcss_requires_frequency(self):
        squelch = self.valid_squelch()
        squelch["method"] = "ctcss"

        self.assertIn(
            "CTCSS frequency is required",
            " ".join(self.errors(squelch)),
        )

        squelch = self.valid_squelch()
        squelch.update({
            "advanced_example": "combine",
            "combine_components": [
                "ctcss",
                "siglev",
            ],
        })

        self.assertIn(
            "CTCSS frequency is required",
            " ".join(self.errors(squelch)),
        )

    def test_ctcss_sql_disables_tx_ctcss(self):
        squelch = self.valid_squelch()
        squelch.update({
            "method": "ctcss",
            "ctcss_freq": "88.5",
            "ctcss_tx": True,
        })

        self.assertIn(
            "cannot use TX CTCSS",
            " ".join(self.errors(squelch)),
        )

    def test_single_port_model_uses_detailed_validation(self):
        model = new_node_model()
        model["node"].update({
            "type": "simplex",
            "callsign": "TEST",
        })
        model["squelch"].update({
            "advanced_example": "combine",
            "combine_components": ["vox"],
        })

        errors = validate_model(model)

        self.assertIn(
            "Squelch COMBINE requires at least two "
            "detector components.",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
    