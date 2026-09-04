#!/usr/bin/env python3

"""
Node model persistence for SvxLink Dashboard V3.1.
"""

import json
from pathlib import Path
from copy import deepcopy
from models.node_model import DEFAULT_MODEL, new_node_model
from hw_platforms import get_platform_profile
from services.svxlink_config_discovery import discover_macros


APP_ROOT = Path("/opt/dashboard")
CONFIG_DIR = APP_ROOT / "config"
MODEL_FILE = CONFIG_DIR / "node_model.json"
FEDERATION_HOST_IDS = {
    "north.america.svxlink.net": "north_america",
    "uk.wide.svxlink.uk": "ukwide",
    "australia.svxlink.net": "australia_nz",
    "yorkshire.svxlink.uk": "yorkshire",
}
CTCSS_TONES = [
    ("", "None / disabled"),
    ("67.0", "67.0 Hz"),
    ("69.3", "69.3 Hz"),
    ("71.9", "71.9 Hz"),
    ("74.4", "74.4 Hz"),
    ("77.0", "77.0 Hz"),
    ("79.7", "79.7 Hz"),
    ("82.5", "82.5 Hz"),
    ("85.4", "85.4 Hz"),
    ("88.5", "88.5 Hz"),
    ("91.5", "91.5 Hz"),
    ("94.8", "94.8 Hz"),
    ("97.4", "97.4 Hz"),
    ("100.0", "100.0 Hz"),
    ("103.5", "103.5 Hz"),
    ("107.2", "107.2 Hz"),
    ("110.9", "110.9 Hz"),
    ("114.8", "114.8 Hz"),
    ("118.8", "118.8 Hz"),
    ("123.0", "123.0 Hz"),
    ("127.3", "127.3 Hz"),
    ("131.8", "131.8 Hz"),
    ("136.5", "136.5 Hz"),
    ("141.3", "141.3 Hz"),
    ("146.2", "146.2 Hz"),
    ("151.4", "151.4 Hz"),
    ("156.7", "156.7 Hz"),
    ("159.8", "159.8 Hz"),
    ("162.2", "162.2 Hz"),
    ("165.5", "165.5 Hz"),
    ("167.9", "167.9 Hz"),
    ("171.3", "171.3 Hz"),
    ("173.8", "173.8 Hz"),
    ("177.3", "177.3 Hz"),
    ("179.9", "179.9 Hz"),
    ("183.5", "183.5 Hz"),
    ("186.2", "186.2 Hz"),
    ("189.9", "189.9 Hz"),
    ("192.8", "192.8 Hz"),
    ("196.6", "196.6 Hz"),
    ("199.5", "199.5 Hz"),
    ("203.5", "203.5 Hz"),
    ("206.5", "206.5 Hz"),
    ("210.7", "210.7 Hz"),
    ("218.1", "218.1 Hz"),
    ("225.7", "225.7 Hz"),
    ("229.1", "229.1 Hz"),
    ("233.6", "233.6 Hz"),
    ("241.8", "241.8 Hz"),
    ("250.3", "250.3 Hz"),
    ("254.1", "254.1 Hz"),
]


def normalise_ctcss_tone(value):
    value = str(value or "").strip()

    valid_values = {
        tone_value
        for tone_value, _label in CTCSS_TONES
    }

    if value in valid_values:
        return value

    return ""

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def create_default_model():
    platform = get_platform_profile()
    return new_node_model(platform=platform)

def merge_missing_defaults(model, defaults=None):
    """
    Add missing default values without replacing saved configuration.

    Returns True when the model was changed.
    """

    if defaults is None:
        defaults = DEFAULT_MODEL

    changed = False

    for key, default_value in defaults.items():
        if key not in model:
            model[key] = deepcopy(default_value)
            changed = True
            continue

        saved_value = model[key]

        if isinstance(saved_value, dict) and isinstance(default_value, dict):
            if merge_missing_defaults(saved_value, default_value):
                changed = True

    return changed

def migrate_node_model(model):
    """
    Migrate an existing saved model to the current schema.

    Existing values are retained. Legacy fields remain available until
    all renderers and configuration pages have moved to schema version 2.
    """

    try:
        schema_version = int(model.get("schema_version", 1))
    except (TypeError, ValueError):
        schema_version = 1

    if schema_version >= 2:
        return merge_missing_defaults(model)

    legacy_reflector = deepcopy(model.get("reflector", {}))
    legacy_courtesy = deepcopy(model.get("courtesy", {}))
    legacy_repeater = deepcopy(model.get("repeater", {}))

    enabled_ports = [
        str(port)
        for port in model.get("ports", {}).get("enabled", [])
    ]

    nodes = model.get("nodes", {})
    hardware = model.get("hardware", {})

    is_multiport = (
        hardware.get("family") == "ics"
        or len(enabled_ports) > 1
    )

    port_courtesy = {}

    if is_multiport and enabled_ports:
        first_node = nodes.get(enabled_ports[0], {})
        port_courtesy = deepcopy(first_node.get("courtesy", {}))

    merge_missing_defaults(model)

    if is_multiport and enabled_ports:
        model["installation"]["primary_port_id"] = enabled_ports[0]

    courtesy_source = port_courtesy or legacy_courtesy

    courtesy_mode = courtesy_source.get(
        "mode",
        model["tones"]["courtesy_mode"],
    )

    courtesy_frequency = courtesy_source.get(
        "frequency",
        legacy_courtesy.get(
            "frequency",
            model["tones"]["courtesy_frequency"],
        ),
    )

    idle_mode = courtesy_source.get(
        "idle_tone",
        legacy_repeater.get(
            "idle_tone",
            model["tones"]["idle_mode"],
        ),
    )

    closedown_mode = courtesy_source.get(
        "down_tone",
        legacy_repeater.get(
            "down_tone",
            model["tones"]["closedown_mode"],
        ),
    )

    if idle_mode == "none":
        idle_mode = "silence"

    model["tones"] = {
        "courtesy_mode": courtesy_mode,
        "courtesy_frequency": courtesy_frequency,
        "idle_mode": idle_mode,
        "closedown_mode": closedown_mode,
    }

    model.setdefault("build", {})
    model["build"]["tones_configured"] = True

    reflector_enabled = bool(
        legacy_reflector.get("enabled")
    )

    model["reflector"]["enabled"] = reflector_enabled

    if reflector_enabled:
        legacy_host = str(
            legacy_reflector.get("host") or ""
        ).strip()

        federation_id = FEDERATION_HOST_IDS.get(legacy_host)

        if federation_id:
            model["reflector"]["route"] = "federation"
            model["reflector"]["federation"]["network_id"] = federation_id
            model["reflector"]["federation"]["auth_key"] = (
                legacy_reflector.get("auth_key")
            )
        else:
            model["reflector"]["route"] = "v2"
            model["reflector"]["v2"].update({
                "name": legacy_reflector.get("name"),
                "host": legacy_reflector.get("host"),
                "port": legacy_reflector.get("port"),
                "auth_key": legacy_reflector.get("auth_key"),
                "default_tg": legacy_reflector.get("default_tg", 0),
                "monitor_tgs": legacy_reflector.get("monitor_tgs", []),
            })
    else:
        model["reflector"]["route"] = "none"

    if is_multiport and enabled_ports:
        if reflector_enabled:
            model["topology"]["reflector_link"]["ports"] = list(
                enabled_ports
            )
            model["topology"]["independent_ports"] = []
        else:
            model["topology"]["reflector_link"]["ports"] = []
            model["topology"]["independent_ports"] = list(
                enabled_ports
            )

    model["schema_version"] = 2

    return True

def save_node_model(model):
    ensure_config_dir()

    MODEL_FILE.write_text(
        json.dumps(model, indent=4),
        encoding="utf-8",
    )


def load_node_model():
    ensure_config_dir()

    if not MODEL_FILE.exists() or MODEL_FILE.stat().st_size == 0:
        model = create_default_model()
        save_node_model(model)
        return model

    try:
        model = json.loads(
            MODEL_FILE.read_text(encoding="utf-8")
        )

        model_changed = migrate_node_model(model)

        if "macros" not in model:
            try:
                model["macros"] = discover_macros()
            except FileNotFoundError:
                model["macros"] = {}

            model_changed = True

        if model_changed:
            save_node_model(model)

        return model

    except json.JSONDecodeError:
        corrupt_file = MODEL_FILE.with_suffix(".json.corrupt")
        MODEL_FILE.rename(corrupt_file)

        model = create_default_model()
        save_node_model(model)
        return model

def reset_node_model():
    model = create_default_model()
    save_node_model(model)
    return model