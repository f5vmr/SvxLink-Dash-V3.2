"""Resolve topology radio identities without changing saved model structure."""


def get_topology_ports(model):
    """Return port ID -> logic name for established renderer configurations.

    An ordinary single radio uses virtual ID '1' when no hardware-port list
    exists. This does not create nodes, choose memberships or change rendering.
    Raise ValueError for ambiguous or unfinished configurations.
    """
    hardware = model.get("hardware", {})
    profile_id = (model.get("hardware_profile_id") or hardware.get("profile_id")
                  or hardware.get("id") or hardware.get("profile") or "")
    is_ics = hardware.get("family") == "ics" or str(profile_id).startswith("ics_")
    ports = model.get("ports", {})
    enabled = ports.get("enabled") if isinstance(ports, dict) else None
    if enabled is None and not is_ics and "ports" not in model:
        enabled = ["1"]
    if not isinstance(enabled, list) or not enabled:
        raise ValueError("Select at least one enabled radio port.")
    if any(not isinstance(port, str) or not port for port in enabled):
        raise ValueError("Radio-port IDs must be non-empty strings.")
    if len(set(enabled)) != len(enabled):
        raise ValueError("Enabled radio-port IDs must be unique.")
    if is_ics or len(enabled) > 1:
        return {
            port: "Port{}Logic".format(port)
            for port in enabled
        }

    role = model.get("node", {}).get("type")
    if role not in ("simplex", "repeater"):
        raise ValueError("Select the single radio's simplex or repeater role.")
    return {enabled[0]: "RepeaterLogic" if role == "repeater" else "SimplexLogic"}


def get_topology_logic_name(model, port_id):
    """Resolve an enabled port; never silently substitute another port."""
    ports = get_topology_ports(model)
    if not isinstance(port_id, str) or port_id not in ports:
        raise ValueError("Port {!r} is not an enabled topology port.".format(port_id))
    return ports[port_id]
