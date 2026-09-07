#!/usr/bin/env python3

"""
Shared guided transmitter-setting validation.
"""


def parse_tx_delay(
    value,
    label="TX delay",
):
    """
    Return (delay, errors).

    TX delay is expressed in milliseconds and must be
    an integer from 0 through 1000.
    """

    text = str(
        500 if value is None else value
    ).strip()

    try:
        delay = int(text)
    except (TypeError, ValueError):
        return None, [
            f"{label} must be a whole number from "
            "0 to 1000 milliseconds."
        ]

    if delay < 0 or delay > 1000:
        return None, [
            f"{label} must be between 0 and "
            "1000 milliseconds."
        ]

    return delay, []