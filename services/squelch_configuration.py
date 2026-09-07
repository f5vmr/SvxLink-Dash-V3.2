#!/usr/bin/env python3

"""
Shared guided squelch-form parsing.

Standard detectors are active. Advanced and specialist selections
describe commented manual examples only.
"""

from models.node_model import (
    squelch_uses_ctcss,
    validate_squelch_configuration,
)


def parse_squelch_form(
    form,
    allowed_methods,
    valid_ctcss_values,
    label="Squelch",
):
    """
    Return (squelch, errors) without modifying an existing model.
    """

    method = str(
        form.get("squelch_method") or ""
    ).strip().lower()

    advanced_example = str(
        form.get("advanced_example") or ""
    ).strip().lower() or None

    manual_detector = str(
        form.get("manual_detector") or ""
    ).strip().lower() or None

    combine_components = [
        str(component).strip().lower()
        for component in form.getlist(
            "combine_components"
        )
        if str(component).strip()
    ]

    if advanced_example != "combine":
        combine_components = []

    squelch = {
        "method": method,
        "advanced_example": advanced_example,
        "combine_components": combine_components,
        "manual_detector": manual_detector,
        "ctcss_freq": None,
        "ctcss_tx": (
            method == "ctcss"
            and str(
                form.get("ctcss_tx") or ""
            ).strip().lower() == "yes"
        ),
    }

    errors = []

    if method not in set(allowed_methods):
        errors.append(
            f"{label} active detector is not available "
            "for this hardware."
        )

    ctcss_freq = str(
        form.get("ctcss_freq") or ""
    ).strip()

    if squelch_uses_ctcss({
        **squelch,
        "ctcss_freq": ctcss_freq or None,
    }):
        if ctcss_freq in set(valid_ctcss_values):
            squelch["ctcss_freq"] = ctcss_freq
        elif ctcss_freq:
            errors.append(
                f"{label} CTCSS frequency is invalid."
            )

    errors.extend(
        validate_squelch_configuration(
            squelch,
            label,
        )
    )

    return squelch, errors
