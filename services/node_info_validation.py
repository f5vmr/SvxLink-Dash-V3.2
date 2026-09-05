#!/usr/bin/env python3

"""
Validation helpers for public node information and LocationInfo.

This module contains validation policy only. It does not save the
node model or render configuration files.
"""

import re


DMS_PATTERN = re.compile(
    r"^"
    r"(\d{1,3})"
    r"\."
    r"(\d{1,2})"
    r"\."
    r"(\d{1,2}(?:\.\d+)?)"
    r"([NSEW])"
    r"$",
    re.IGNORECASE,
)

MAIDENHEAD_PATTERN = re.compile(
    r"^[A-R]{2}\d{2}(?:[A-X]{2}(?:\d{2})?)?$",
    re.IGNORECASE,
)

TX_POWER_PATTERN = re.compile(
    r"^"
    r"(\d+(?:\.\d+)?)"
    r"\s*"
    r"(?:W|WATT|WATTS)?"
    r"$",
    re.IGNORECASE,
)


def _number(value):
    """
    Convert a form/model value to float, returning None when invalid.
    """

    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _integer(value):
    """
    Convert a form/model value to an exact integer.
    """

    try:
        text = str(value).strip()

        if not text:
            return None

        numeric = float(text)

        if not numeric.is_integer():
            return None

        return int(numeric)

    except (TypeError, ValueError):
        return None


def validate_dms(value, coordinate):
    """
    Validate one SvxLink DMS coordinate.

    Accepted examples:
        55.10.51N
        01.32.45W
        55.10.51.5N

    coordinate must be "latitude" or "longitude".
    """

    text = str(value or "").strip().upper()

    if not text:
        return f"{coordinate.title()} DMS is required."

    match = DMS_PATTERN.fullmatch(text)

    if not match:
        return (
            f"{coordinate.title()} DMS must use SvxLink format, "
            "for example 55.10.51N or 01.32.45W."
        )

    degrees = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    direction = match.group(4).upper()

    if coordinate == "latitude":
        maximum_degrees = 90
        valid_directions = {"N", "S"}
    elif coordinate == "longitude":
        maximum_degrees = 180
        valid_directions = {"E", "W"}
    else:
        raise ValueError(
            "coordinate must be latitude or longitude"
        )

    if direction not in valid_directions:
        return (
            f"{coordinate.title()} DMS must end with "
            f"{'N or S' if coordinate == 'latitude' else 'E or W'}."
        )

    if degrees > maximum_degrees:
        return (
            f"{coordinate.title()} degrees must not exceed "
            f"{maximum_degrees}."
        )

    if minutes >= 60:
        return (
            f"{coordinate.title()} DMS minutes must be below 60."
        )

    if seconds >= 60:
        return (
            f"{coordinate.title()} DMS seconds must be below 60."
        )

    if degrees == maximum_degrees and (
        minutes != 0 or seconds != 0
    ):
        return (
            f"{coordinate.title()} at {maximum_degrees} degrees "
            "must use zero minutes and seconds."
        )

    return None


def validate_node_information(node_info, location_info=None):
    """
    Validate node_info and optional LocationInfo settings.

    Returns:
        list[str]: validation messages, empty when valid.

    Ordinary node information fields are validated when populated.
    LocationInfo-specific required fields are enforced only when
    LocationInfo is enabled.
    """

    node_info = node_info or {}
    location_info = location_info or {}

    errors = []

    latitude_text = str(
        node_info.get("lat") or ""
    ).strip()

    if latitude_text:
        latitude = _number(latitude_text)

        if latitude is None:
            errors.append(
                "Decimal latitude must be a number."
            )
        elif latitude < -90 or latitude > 90:
            errors.append(
                "Decimal latitude must be between -90 and 90."
            )

    longitude_text = str(
        node_info.get("long") or ""
    ).strip()

    if longitude_text:
        longitude = _number(longitude_text)

        if longitude is None:
            errors.append(
                "Decimal longitude must be a number."
            )
        elif longitude < -180 or longitude > 180:
            errors.append(
                "Decimal longitude must be between -180 and 180."
            )

    locator = str(
        node_info.get("locator") or ""
    ).strip().upper()

    if locator and not MAIDENHEAD_PATTERN.fullmatch(locator):
        errors.append(
            "Maidenhead locator must contain 4, 6 or 8 valid "
            "locator characters."
        )

    for label, field_name in (
        ("RX frequency", "rx_freq"),
        ("TX frequency", "tx_freq"),
    ):
        frequency_text = str(
            node_info.get(field_name) or ""
        ).strip()

        if not frequency_text:
            continue

        frequency = _number(frequency_text)

        if frequency is None or frequency <= 0:
            errors.append(
                f"{label} must be a positive number in MHz."
            )

    tx_power_text = str(
        node_info.get("tx_power") or ""
    ).strip()

    if tx_power_text:
        power_match = TX_POWER_PATTERN.fullmatch(
            tx_power_text
        )

        if not power_match:
            errors.append(
                "TX power must be a positive number, optionally "
                "followed by W, Watt or Watts."
            )
        elif float(power_match.group(1)) <= 0:
            errors.append(
                "TX power must be greater than zero."
            )

    antenna_height_text = str(
        node_info.get("antenna_height") or ""
    ).strip()

    if antenna_height_text:
        antenna_height = _number(
            antenna_height_text
        )

        if antenna_height is None or antenna_height < 0:
            errors.append(
                "Antenna height must be zero or a positive number."
            )

    antenna_direction = str(
        node_info.get("antenna_direction") or ""
    ).strip().lower()

    if antenna_direction and antenna_direction != "omni":
        direction = _integer(antenna_direction)

        if direction is None or direction < 0 or direction > 359:
            errors.append(
                "Antenna direction must be omni or a bearing "
                "between 0 and 359 degrees."
            )

    if not location_info.get("enabled"):
        return errors

    latitude_dms_error = validate_dms(
        node_info.get("lat_dms"),
        "latitude",
    )

    if latitude_dms_error:
        errors.append(latitude_dms_error)

    longitude_dms_error = validate_dms(
        node_info.get("long_dms"),
        "longitude",
    )

    if longitude_dms_error:
        errors.append(longitude_dms_error)

    if not str(
        location_info.get("aprs_server_list") or ""
    ).strip():
        errors.append(
            "An APRS server is required when LocationInfo is enabled."
        )

    if not str(
        node_info.get("tx_freq") or ""
    ).strip():
        errors.append(
            "TX frequency is required when LocationInfo is enabled."
        )

    if not tx_power_text:
        errors.append(
            "TX power is required when LocationInfo is enabled."
        )

    if not antenna_height_text:
        errors.append(
            "Antenna height is required when LocationInfo is enabled."
        )

    antenna_gain = _number(
        location_info.get("antenna_gain")
    )

    if antenna_gain is None:
        errors.append(
            "Antenna gain must be a number in dBd when "
            "LocationInfo is enabled."
        )

    height_unit = str(
        location_info.get("antenna_height_unit") or ""
    ).strip().lower()

    if height_unit not in {"m", "feet"}:
        errors.append(
            "Antenna height unit must be metres or feet."
        )

    tx_offset = _integer(
        location_info.get("tx_offset_khz")
    )

    if tx_offset is None:
        errors.append(
            "TX offset must be a whole signed number in kHz."
        )

    beacon_interval = _integer(
        location_info.get("beacon_interval")
    )

    if (
        beacon_interval is None
        or beacon_interval < 1
        or beacon_interval > 1440
    ):
        errors.append(
            "Beacon interval must be between 1 and 1440 minutes."
        )

    comment = str(
        location_info.get("comment") or ""
    ).strip()

    if len(comment) > 36:
        errors.append(
            "LocationInfo comment must not exceed 36 characters."
        )

    advertised_ctcss = str(
        location_info.get("advertised_ctcss") or ""
    ).strip()

    if advertised_ctcss:
        ctcss = _number(advertised_ctcss)

        if ctcss is None or ctcss <= 0:
            errors.append(
                "Advertised CTCSS must be a positive frequency "
                "or left empty."
            )

    if (
        location_info.get("publish_echolink_status")
        and not str(
            location_info.get("status_server_list") or ""
        ).strip()
    ):
        errors.append(
            "An EchoLink status server is required when status "
            "publication is enabled."
        )

    return errors