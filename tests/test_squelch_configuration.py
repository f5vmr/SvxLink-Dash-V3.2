#!/usr/bin/env python3

import unittest

from werkzeug.datastructures import MultiDict

from services.squelch_configuration import (
    parse_squelch_form,
)


STANDARD_METHODS = {
    "hidraw",
    "gpiod",
    "serial",
    "ctcss",
}

CTCSS_VALUES = {
    "67.0",
    "88.5",
    "123.0",
}


class SquelchFormTests(unittest.TestCase):

    def parse(self, values, allowed=None):
        return parse_squelch_form(
            MultiDict(values),
            allowed or STANDARD_METHODS,
            CTCSS_VALUES,
            "Port 2 squelch",
        )

    def test_standard_detector_is_active(self):
        squelch, errors = self.parse({
            "squelch_method": "gpiod",
        })

        self.assertEqual(errors, [])
        self.assertEqual(
            squelch["method"],
            "gpiod",
        )
        self.assertIsNone(
            squelch["advanced_example"]
        )
        self.assertIsNone(
            squelch["manual_detector"]
        )

    def test_hardware_restriction_is_enforced(self):
        _squelch, errors = self.parse(
            {
                "squelch_method": "hidraw",
            },
            allowed={"gpiod", "ctcss"},
        )

        self.assertIn(
            "not available for this hardware",
            " ".join(errors),
        )

    def test_vox_is_a_commented_example(self):
        squelch, errors = self.parse({
            "squelch_method": "serial",
            "advanced_example": "vox",
        })

        self.assertEqual(errors, [])
        self.assertEqual(
            squelch["method"],
            "serial",
        )
        self.assertEqual(
            squelch["advanced_example"],
            "vox",
        )

    def test_valid_combine_preserves_components(self):
        squelch, errors = self.parse([
            ("squelch_method", "gpiod"),
            ("advanced_example", "combine"),
            ("combine_components", "vox"),
            ("combine_components", "siglev"),
        ])

        self.assertEqual(errors, [])
        self.assertEqual(
            squelch["combine_components"],
            ["vox", "siglev"],
        )

    def test_combine_ctcss_requires_valid_frequency(self):
        _squelch, errors = self.parse([
            ("squelch_method", "gpiod"),
            ("advanced_example", "combine"),
            ("combine_components", "ctcss"),
            ("combine_components", "siglev"),
            ("ctcss_freq", "999.9"),
        ])

        self.assertIn(
            "CTCSS frequency is invalid",
            " ".join(errors),
        )

    def test_specialist_selection_remains_separate(self):
        squelch, errors = self.parse({
            "squelch_method": "hidraw",
            "manual_detector": "evdev",
        })

        self.assertEqual(errors, [])
        self.assertEqual(
            squelch["method"],
            "hidraw",
        )
        self.assertEqual(
            squelch["manual_detector"],
            "evdev",
        )

    def test_advanced_and_specialist_are_exclusive(self):
        _squelch, errors = self.parse({
            "squelch_method": "hidraw",
            "advanced_example": "siglev",
            "manual_detector": "pty",
        })

        self.assertIn(
            "cannot select both",
            " ".join(errors),
        )


if __name__ == "__main__":
    unittest.main()