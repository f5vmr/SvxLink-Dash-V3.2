#!/usr/bin/env python3

import unittest

from services.transmitter_configuration import (
    parse_tx_delay,
)


class TransmitterConfigurationTests(unittest.TestCase):

    def test_default_delay(self):
        delay, errors = parse_tx_delay(None)

        self.assertEqual(delay, 500)
        self.assertEqual(errors, [])

    def test_valid_delay_range(self):
        for value, expected in (
            ("0", 0),
            ("500", 500),
            ("1000", 1000),
        ):
            with self.subTest(value=value):
                delay, errors = parse_tx_delay(value)

                self.assertEqual(delay, expected)
                self.assertEqual(errors, [])

    def test_non_numeric_delay_is_rejected(self):
        delay, errors = parse_tx_delay("slow")

        self.assertIsNone(delay)
        self.assertIn(
            "whole number",
            " ".join(errors),
        )

    def test_out_of_range_delay_is_rejected(self):
        for value in ("-1", "1001"):
            with self.subTest(value=value):
                delay, errors = parse_tx_delay(value)

                self.assertIsNone(delay)
                self.assertIn(
                    "between 0 and 1000",
                    " ".join(errors),
                )


if __name__ == "__main__":
    unittest.main()