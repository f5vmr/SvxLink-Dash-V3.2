#!/usr/bin/env python3

"""
SvxLink-Dash-V3.1 node model.

This file defines the authoritative configuration model used by:
- Flask setup pages
- validation logic
- svxlink.conf renderers
- future dashboard editing
"""

from copy import deepcopy


SUPPORTED_NODE_TYPES = {"simplex", "repeater"}

SUPPORTED_IDENT_MODES = {
    "none",
    "cw",
    "voice",
    "both",
}

SUPPORTED_ROGER_MODES = {
    "none",
    "beep",
    "morse_t",
    "morse_k",
}
SUPPORTED_IDLE_TONES = {
    "chime",
    "pip",
    "silence",
}

SUPPORTED_DOWN_TONES = {
    "biboop",
    "va",
    "none",
}
SUPPORTED_SQUELCH_METHODS = [
    "hidraw",
    "gpiod",
    "ctcss",
    "serial",
]
SUPPORTED_INTERFACE_MODES = {
    "hidraw",
    "gpiod",
    "hybrid",
    "serial",
}
NANOPI_NEO_GPIO_DEFAULTS = {
    "sql": {
        "chip": "gpiochip0",
        "line": 203,
        "active": "high",
    },
    "ptt": {
        "chip": "gpiochip0",
        "line": 6,
    },
}
DEFAULT_MODEL = {
    "schema_version": 2,

    "build": {
        "intent": "single_channel",
    },

    "installation": {
        "primary_port_id": None,
    },

    "platform": {
        "id": None,
        "name": None,
        "supported": False,
    },

    "node": {
        "type": None,
        "callsign": None,
        "language": "en_US",
    },
    "interface": {
        "mode": "hidraw",
        "sql_source": "hidraw",
        "ptt_source": "hidraw",
    },
    "reflector": {
        "enabled": False,
        "route": "none",

        # Legacy Protocol 2 fields retained during migration.
        "name": None,
        "host": None,
        "port": None,
        "auth_key": None,

        "federation": {
            "network_id": None,
            "auth_key": None,
        },

        "v2": {
            "name": None,
            "host": None,
            "port": None,
            "auth_key": None,
            "default_tg": 0,
            "monitor_tgs": [],
        },

        "v3": {
            "name": None,
            "host": None,
            "port": None,
            "default_tg": 0,
            "monitor_tgs": [],
            "subject": {
                "given_name": None,
                "surname": None,
                "organizational_unit": None,
                "organization": None,
                "locality": None,
                "state_or_province": None,
                "country": None,
                "email": None,
            },
        },
    },

    "topology": {
        "reflector_link": {
            "name": "LinkToReflector",
            "ports": [],
            "default_active": True,
            "timeout": 300,
        },
        "local_links": [],
        "independent_ports": [],
    },
        "node_info": {
            "nodeLocation": "",
            "hidden": False,
            "qth_name": "",
            "sysop": "",
            "lat": "",
            "long": "",
            "locator": "",
            "lat_dms": "",
            "long_dms": "",
            "rx_freq": "",
            "tx_freq": "",
            "tx_power": "",
            "antenna": "",
            "antenna_height": "",
            "antenna_direction": "omni",
        },

        "location_info": {
            "enabled": False,
            "aprs_server_list": "",
            "publish_echolink_status": False,
            "status_server_list": "aprs.echolink.org:5199",
            "narrow": True,
            "tx_offset_khz": 0,
            "antenna_gain": "",
            "antenna_height_unit": "m",
            "advertised_ctcss": "",
            "beacon_interval": 10,
            "comment": "",
        },
        "ident": {
            "short": {
            "mode": "cw",
            "interval": 15,
        },
        "long": {
            "mode": "voice",
            "interval": 60,
        },
    },
    "gpio": {
        "sql": {
            "chip": "gpiochip0",
            "line": 23,
            "active": "high",
        },
        "ptt": {
            "chip": "gpiochip0",
            "line": 24,
        },
    },
    "hidraw": {
        "device": "/dev/hidraw0",
        "sql_pin": "VOL_DN",
        "ptt_pin": "GPIO3",
    },
    "serial": {
        "sql_port": "/dev/ttyS0",
        "sql_pin": "CTS",
        "sql_set_pins": "DTR!RTS",
        "ptt_port": "/dev/ttyS0",
        "ptt_pin": "DTRRTS",
    },
    "cw": {
        "amp": -10,
        "pitch": 650,
        "cpm": 95,
    },
    "audio": {
        "audio_dev": "alsa:plughw:0",
        "audio_channel": 0,
    },
    "time_format": "24",
    "fx_gain_normal": 0,
    "fx_gain_low": -12,
    "sql_hangtime": 20,
    "sql_tail_elim": 270,
    "tg_timeout": 60,
    "tx_ctcss_mode": "ALWAYS",
    "online_control": {
        "enabled": False,
        "command": None,
    },
    "tones": {
        "courtesy_mode": "none",
        "courtesy_frequency": 800,
        "idle_mode": "chime",
        "closedown_mode": "biboop",
    },
    "courtesy": {
        "mode": "none",
    },
    "repeater": {
    "idle_tone": "chime",
    "down_tone": "biboop",
    "idle_timeout": 10,
    "sql_timeout": 180,
    },
    "squelch": {
        "method": "hidraw",
        "ctcss_freq": None,
        "ctcss_tx": False,
    },
    "echolink": {
        "enabled": False,
        "callsign": None,
        "password": None,
        "sysopname": None,
        "location": None,
    },
        "metar": {
            "enabled": False,
            "region": None,
            "startdefault": None,
            "airports": [],
            "custom_startdefault": None,
    },  
        "modules": {
            "enabled": [
            "ModuleHelp",
            "ModuleParrot",
        ],
    },
}

def new_node_model(platform=None):
    """
    Return a fresh node model.

    platform may be a dict from the platform detection layer.
    """

    model = deepcopy(DEFAULT_MODEL)

    if platform is not None:
        platform_id = platform.get("id")

        model["platform"] = {
            "id": platform_id,
            "name": platform.get("name"),
            "supported": bool(platform.get("supported")),
        }

        if platform_id == "nanopi_neo":
            model["gpio"] = deepcopy(NANOPI_NEO_GPIO_DEFAULTS)

    return model
def is_ics_multiport_model(model):
    hardware = model.get("hardware", {})
    enabled_ports = model.get("ports", {}).get("enabled", [])

    return (
        hardware.get("family") == "ics"
        and len(enabled_ports)
    )
def is_multiport_model(model):
    enabled_ports = model.get("ports", {}).get("enabled", [])

    return (
        is_ics_multiport_model(model)
        or len(enabled_ports) > 1
    )
def validate_model(model):
    """
    Validate high-level model consistency.

    Returns:
        list[str]: validation error messages.
    """

    errors = []
    
    multiport = is_multiport_model(model)

    node_type = model.get("node", {}).get("type")
    callsign = model.get("node", {}).get("callsign")

    if multiport:
        nodes = model.get("nodes", {})
        enabled_ports = model.get("ports", {}).get("enabled", [])

        if not enabled_ports:
            errors.append("At least one port must be enabled.")

        if not nodes:
            errors.append("Port configuration is required.")

        for port in enabled_ports:
            port_id = str(port)
            node = nodes.get(port_id, {})

            if node.get("role") not in ("simplex", "repeater"):
                errors.append(
                    f"Port {port_id} type must be simplex or repeater."
                )

            if not node.get("callsign"):
                errors.append(
                    f"Port {port_id} callsign is required."
                )

    else:
        if node_type not in SUPPORTED_NODE_TYPES:
            errors.append("Node type must be simplex or repeater.")

        if not callsign:
            errors.append("Callsign is required.")

    short_ident = model.get("ident", {}).get("short", {})
    long_ident = model.get("ident", {}).get("long", {})

    if short_ident.get("mode") not in SUPPORTED_IDENT_MODES:
        errors.append("Short ident mode is invalid.")

    if long_ident.get("mode") not in SUPPORTED_IDENT_MODES:
        errors.append("Long ident mode is invalid.")

    for ident_name, ident_data in (
        ("Short", short_ident),
        ("Long", long_ident),
    ):
        interval = ident_data.get("interval")

        if not isinstance(interval, int):
            errors.append(f"{ident_name} ident interval must be a number.")
        elif interval < 1:
            errors.append(f"{ident_name} ident interval must be at least 1 minute.")

    tones = get_installation_tones(model)

    courtesy_mode = tones["courtesy_mode"]
    courtesy_frequency = tones["courtesy_frequency"]
    idle_mode = tones["idle_mode"]
    closedown_mode = tones["closedown_mode"]

    if courtesy_mode not in SUPPORTED_ROGER_MODES:
        errors.append("Courtesy tone mode is invalid.")

    if (
        not isinstance(courtesy_frequency, int)
        or isinstance(courtesy_frequency, bool)
        or courtesy_frequency < 300
        or courtesy_frequency > 3000
    ):
        errors.append(
            "Courtesy beep frequency must be between 300 and 3000 Hz."
        )

    if idle_mode not in SUPPORTED_IDLE_TONES:
        errors.append("Idle tone mode is invalid.")

    if closedown_mode not in SUPPORTED_DOWN_TONES:
        errors.append("Close-down tone mode is invalid.")
    
    if not multiport:
        interface_mode = model.get("interface", {}).get("mode")

        if interface_mode not in SUPPORTED_INTERFACE_MODES:
            errors.append("Interface mode is invalid.")

        squelch_method = model.get("squelch", {}).get("method")

        if squelch_method not in SUPPORTED_SQUELCH_METHODS:
            errors.append("Squelch method is invalid.")

    reflector = model.get("reflector", {})

    if reflector.get("enabled"):
        route = str(
            reflector.get("route") or ""
        ).strip().lower()

        if route == "federation":
            federation = reflector.get("federation", {})

            network_id = str(
                federation.get("network_id") or ""
            ).strip()

            auth_key = str(
                federation.get("auth_key") or ""
            )

            if not network_id:
                errors.append(
                    "Federation Family reflector selection is required."
                )

            if len(auth_key) != 16:
                errors.append(
                    "Federation subscription password must be "
                    "exactly 16 characters."
                )

            if not reflector.get("host"):
                errors.append("Reflector host is required.")

            if not reflector.get("port"):
                errors.append("Reflector port is required.")

        elif route == "v2":
            v2 = reflector.get("v2", {})

            host = v2.get("host") or reflector.get("host")
            port = v2.get("port") or reflector.get("port")
            auth_key = (
                v2.get("auth_key")
                or reflector.get("auth_key")
            )

            if not host:
                errors.append("Protocol 2 reflector host is required.")

            if not port:
                errors.append("Protocol 2 reflector port is required.")

            if not auth_key:
                errors.append(
                    "Protocol 2 reflector authentication password "
                    "is required."
                )

        elif route == "v3":
            v3 = reflector.get("v3", {})
            subject = v3.get("subject", {})

            host = v3.get("host") or reflector.get("host")
            port = v3.get("port") or reflector.get("port")

            if not host:
                errors.append("Protocol 3 reflector host is required.")

            if not port:
                errors.append("Protocol 3 reflector port is required.")

            required_subject_fields = {
                "given_name": "given name",
                "surname": "surname",
                "organizational_unit": "organizational unit",
                "organization": "organization",
                "locality": "locality",
                "state_or_province": "state or province",
                "country": "country",
                "email": "email address",
            }

            for field_name, field_label in required_subject_fields.items():
                if not str(subject.get(field_name) or "").strip():
                    errors.append(
                        f"Protocol 3 certificate {field_label} "
                        "is required."
                    )

            country = str(
                subject.get("country") or ""
            ).strip()

            if country and (
                len(country) != 2
                or not country.isalpha()
            ):
                errors.append(
                    "Protocol 3 certificate country must be "
                    "a two-letter code."
                )

            email = str(
                subject.get("email") or ""
            ).strip()

            if email and (
                "@" not in email
                or email.startswith("@")
                or email.endswith("@")
            ):
                errors.append(
                    "Protocol 3 certificate email address is invalid."
                )

        else:
            errors.append(
                "Enabled reflector must use Federation Family, "
                "Protocol 2 or Protocol 3."
            )

    echolink = model.get("echolink", {})

    if echolink.get("enabled"):
        echolink_callsign = echolink.get("callsign")

        if not echolink_callsign:
            errors.append("EchoLink callsign is required.")
        elif not (
            echolink_callsign.endswith("-L")
            or echolink_callsign.endswith("-R")
        ):
            errors.append("EchoLink callsign must end in -L or -R.")

        if not echolink.get("password"):
            errors.append("EchoLink password is required.")

        if not echolink.get("sysopname"):
            errors.append("EchoLink sysop name is required.")

        location = echolink.get("location")

        if not location:
            errors.append("EchoLink location is required.")
        elif not location.startswith("[Svx] "):
            errors.append("EchoLink location must start with [Svx].")
        elif len(location.replace("[Svx] ", "", 1)) > 12:
            errors.append("EchoLink location text must be 12 characters or fewer.")
    
    return errors


def set_node_identity(model, node_type, callsign):
    """
    Set basic node identity.
    """

    model["node"]["type"] = node_type
    model["node"]["callsign"] = callsign.strip().upper()
    return model


def set_ident(model, short_mode, short_interval, long_mode, long_interval):
    """
    Set short and long identification behaviour.
    """

    model["ident"]["short"]["mode"] = short_mode
    model["ident"]["short"]["interval"] = int(short_interval)

    model["ident"]["long"]["mode"] = long_mode
    model["ident"]["long"]["interval"] = int(long_interval)

    return model

def get_installation_tones(model):
    """
    Return normalised installation-wide tone settings.

    Legacy single-port values are used only when the version 2 tone
    structure is absent.
    """

    tones = model.get("tones")

    if isinstance(tones, dict):
        return {
            "courtesy_mode": tones.get("courtesy_mode", "none"),
            "courtesy_frequency": tones.get(
                "courtesy_frequency",
                800,
            ),
            "idle_mode": tones.get("idle_mode", "chime"),
            "closedown_mode": tones.get(
                "closedown_mode",
                "biboop",
            ),
        }

    courtesy = model.get("courtesy", {})
    repeater = model.get("repeater", {})

    idle_mode = repeater.get("idle_tone", "chime")

    if idle_mode == "none":
        idle_mode = "silence"

    return {
        "courtesy_mode": courtesy.get("mode", "none"),
        "courtesy_frequency": courtesy.get("frequency", 800),
        "idle_mode": idle_mode,
        "closedown_mode": repeater.get(
            "down_tone",
            "biboop",
        ),
    }

def set_roger(model, roger_mode):
    """
    Set the installation-wide courtesy tone mode.
    """

    model.setdefault("tones", {})
    model["tones"]["courtesy_mode"] = roger_mode

    return model

def set_interface_mode(model, mode):
    """
    Set physical SQL/PTT control interface.

    gpiod:
        SQL = GPIOD
        PTT = GPIOD

    hidraw:
        SQL = HIDRAW
        PTT = HIDRAW

    hybrid:
        SQL = GPIOD
        PTT = HIDRAW
    """

    if mode == "gpiod":
        model["interface"] = {
            "mode": "gpiod",
            "sql_source": "gpiod",
            "ptt_source": "gpiod",
        }

    elif mode == "hidraw":
        model["interface"] = {
            "mode": "hidraw",
            "sql_source": "hidraw",
            "ptt_source": "hidraw",
        }

    elif mode == "hybrid":
        model["interface"] = {
            "mode": "hybrid",
            "sql_source": "gpiod",
            "ptt_source": "hidraw",
        }

    else:
        raise ValueError(f"Unsupported interface mode: {mode}")

    return model

def set_squelch(model, method, ctcss_freq=None, ctcss_tx=False):
    """
    Set squelch configuration.
    """

    model["squelch"]["method"] = method
    model["squelch"]["ctcss_freq"] = ctcss_freq
    model["squelch"]["ctcss_tx"] = bool(ctcss_tx)

    return model


def enable_reflector(model, name, host, port, auth_key):
    """
    Enable reflector configuration.
    """

    model["reflector"] = {
        "enabled": True,
        "name": name,
        "host": host,
        "port": int(port),
        "auth_key": auth_key,
    }

    return model


def disable_reflector(model):
    """
    Disable reflector configuration.
    """

    model["reflector"] = {
        "enabled": False,
        "name": None,
        "host": None,
        "port": None,
        "auth_key": None,
    }

    return model
    
def set_echolink(
    model,
    enabled,
    callsign=None,
    password=None,
    sysopname=None,
    location=None,
):
    """
    Set EchoLink module configuration.

    EchoLink LOCATION is built as:
        [Svx] Fq, Location

    The final LOCATION field must not exceed 17 characters.
    """

    if not enabled:
        model["echolink"] = {
            "enabled": False,
            "callsign": None,
            "password": None,
            "sysopname": None,           
            "location": None,
        }
        return model

    callsign = callsign.strip().upper()
    password = password.strip()
    sysopname = sysopname.strip()
    location_text = location.strip()

    location = f"[Svx] {location_text}"

    model["echolink"] = {
        "enabled": True,
        "callsign": callsign,
        "password": password,
        "sysopname": sysopname,
        "location": location,
    }

    return model

def enable_module(model, module_name):
    """
    Enable a SvxLink module by name.
    """

    modules = model["modules"]["enabled"]

    if module_name not in modules:
        modules.append(module_name)

    return model


def disable_module(model, module_name):
    """
    Disable a SvxLink module by name.
    """

    modules = model["modules"]["enabled"]

    if module_name in modules:
        modules.remove(module_name)

    return model