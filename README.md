# SvxLink-Dash-V3.2

A modern Flask-based configuration and runtime dashboard for SvxLink systems.

SvxLink-Dash-V3.2 provides:

- Guided SvxLink configuration using SvxLink V26.05.1 from Tobias Blomberg SM0SVX
- Runtime operational dashboard
- Reflector management
- EchoLink and METAR module configuration
- Live reflector activity monitoring
- DTMF talkgroup control
- Macro Installation and editing
- Protected runtime editing environment
- Hardware and system telemetry
- Live log viewer
- Node information generation
- Multi-platform deployment support

The project is intended for both:

1. Existing SvxLink users wanting a modern configuration/dashboard layer

2. Complete appliance-style SvxLink images for Raspberry Pi, NanoPi-Neo, and a build structure for Linux PC and similar systems.
NB the current structure is in English only and presented for the https://ukwide.svxlink.net, https://north.america.svxlink.net and the https://au.svxlink.net Svxreflectors

---

# Features

## Configuration Builder

- Guided SvxLink configuration workflow
- Simplex and repeater node support on multiple ports
- Reflector support
- EchoLink support
- METAR module support
- Courtesy tone / roger tone support
- GPIO and audio configuration
- Node information generation
- Configuration review before deployment

## Runtime Dashboard

- Live node status
- Service monitoring
- Reflector connection state
- Squelch state
- EchoLink activity
- Monitored talkgroups display
- Live reflector activity feed
- DTMF talkgroup buttons
- Manual DTMF command entry
- Hardware telemetry
- Live system log viewer

## Operational Editing

Protected editing environment with authentication:

- Talkgroup buttons
- Monitoring talkgroups
- EchoLink module
- Macro Editing
- METAR module
- Node information

## Deployment Features

- Automatic configuration rendering
- Automatic SvxLink restart
- Backup-aware deployment
- Systemd service support
- Automatic permission correction
- Portable log-path detection

---

# Supported Platforms

Tested platforms currently include:

Raspberry Pi / Raspberry Pi OS Bookworm / Raspberry Pi OS Trixie
NanoPi Neo / Armbian Bookworm
Linux PC Bookworm LTS

Other Debian-based systems may also function correctly.


---

# Browser Support

Tested with:

- Chromium
- Chrome
- Firefox

---

# Installation

## Quick Install

The installer automatically:

- Downloads SvxLink-Dash-V3.2 into `/opt/dashboard`
- Installs required Python packages
- Configures permissions
- Installs the systemd service
- Configures restricted sudo permissions
- Enables and starts the dashboard service

Run:

```bash
cd /tmp
wget https://raw.githubusercontent.com/f5vmr/SvxLink-Dash-V3.2/main/install/install-dashboard.sh
chmod +x install-dashboard.sh
sudo ./install-dashboard.sh
```

After installation:

```text
http://svxlink.local:5000/
```

---

# Existing SvxLink Requirements

SvxLink must already be operational.

Expected components:

```text
SvxLink Version 26.05.1 in this case 
```

The dashboard assumes:

- SvxLink already functions correctly
- `/etc/svxlink` is present
- DTMF PTY control is enabled
- `/dev/shm/....Logic` exists..

---

# Python Dependencies

Installed automatically by the installer.

Equivalent packages:

```bash
python3
python3-flask
python3-jinja2
python3-werkzeug
python3-psutil
```

---

# Log File Detection

The dashboard automatically determines the active SvxLink log file.

Priority:

1. `LOGFILE=` from `/etc/default/svxlink`
2. `/var/log/svxlink.log`
3. `/var/log/svxlink`

This allows compatibility with:

- Standard SvxLink installations
- Appliance-style images
- Custom deployments

---

# Authentication

Runtime editing functions are protected by dashboard authentication.

Public runtime monitoring remains accessible.

Protected pages include:

- Talkgroups
- Monitoring TGs
- EchoLink editing
- METAR editing
- Node information editing
- Log viewer

Dashboard credentials are configured during initial setup.

---

# Forgotten Credentials

Dashboard credentials can be reset locally on the Linux console.

Run:

```bash
sudo /opt/dashboard/tools/reset_dashboard_auth.py
```

---

# Systemd Service

Installed service:

```text
svxlink-dash.service
```

Service user:

```text
svxlink:svxlink
```

The dashboard intentionally runs as the SvxLink user to allow:

- PTY DTMF control
- Configuration deployment
- Runtime management

---

# Restricted sudo Permissions

The installer configures restricted sudo access for:

```text
systemctl restart svxlink
systemctl is-active svxlink
and a number of other functions
```

via:

```text
/etc/sudoers.d/svxlink-dash
```

---

# Runtime Dashboard Overview

The dashboard provides:

## Left Column Operational State

- Node
- Service
- Reflector
- Modules
- Radio Status
- Squelch State
- Monitoring TGs
- Active TGs
- EchoLink Activity
- Uptime

## Main Operational Area

- Live reflector activity feed
- Talkgroup controls
- Manual DTMF command entry

## System Footer

- Hostname
- IP address
- OS information
- Kernel version
- CPU temperature
- Disk usage
- Memory usage

---

# Manual DTMF Commands

## Talkgroups

Prefix TG numbers with:

```text
91
```

Terminate with:

```text
#
```

Example:

```text
91235#
```

## EchoLink

Open module:

```text
2#
```

Then send:

```text
<node>#
```

Exit EchoLink:

```text
##
```

## METAR

Open module:

```text
5#
```

Airport selection examples:

```text
1#
2#
3#
```

Exit METAR:

```text
#
```

---

# Node Information

The dashboard generates:

```text
/etc/svxlink/node_info.json
```

The setup workflow supports:

- Decimal latitude/longitude
- Maidenhead locator
- DMS coordinate formats
- RF information
- Antenna information

Useful locator resource:

https://www.levinecentral.com/ham/grid_square.php

---

# Repository Layout

```text
/opt/dashboard
├── app.py
├── templates/
├── static/
├── services/
├── renderers/
├── install/
├── config/
├── backups/
└── tools/
```

---

# Service Management

## Restart Dashboard

```bash
sudo systemctl restart svxlink-dash
```

## View Dashboard Status

```bash
sudo systemctl status svxlink-dash
```

## Restart SvxLink

```bash
sudo systemctl restart svxlink
```

---

# Troubleshooting

## Dashboard Does Not Start

Check:

```bash
sudo systemctl status svxlink-dash
```

## Live Log Viewer

The dashboard includes a protected live log viewer.

Alternatively:

```bash
tail -f /var/log/svxlink.log
```

or the configured log file from:

```text
/etc/default/svxlink
```

## DTMF Buttons Not Working

Verify:

```text
/dev/shm/simplex_dtmf_ctrl or /dev/shm/repeater_dtmf_ctrl
```

exists and is writable by user `svxlink`.

# Logic and Link Topology

SvxLink-Dash supports single-port and multi-port installations containing SimplexLogic, RepeaterLogic and ReflectorLogic instances.

## Logic Declaration

Every configured logic instance must be declared in the `[GLOBAL]` section.

Example:

```ini
[GLOBAL]
LOGICS=SimplexLogic1,RepeaterLogic2,SimplexLogic3,SimplexLogic4,ReflectorLogic
LINKS=LinkToReflector,Link34
```

The `LOGICS` entry determines which logic instances SvxLink creates when it starts.

The `LINKS` entry identifies the link sections used to connect selected logic instances together.

Declaring a logic does not automatically connect it to another logic.

## Link Membership

Each link section uses `CONNECT_LOGICS` to specify its exact membership.

A logic omitted from a link remains operational but does not participate in that link.

Example reflector link:

```ini
[LinkToReflector]
CONNECT_LOGICS=SimplexLogic1:9,RepeaterLogic2:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

In this example:

* SimplexLogic1 is connected to the reflector.
* RepeaterLogic2 is connected to the reflector.
* The `:9` suffix is required on each participating radio logic so that DTMF can control reflector talkgroups.
* Other configured radio logics remain outside the reflector link.

## Single-Port Topology

A single-port installation has a simple reflector choice:

* Local operation without ReflectorLogic.
* Local operation linked to ReflectorLogic.

When reflector access is enabled, the single SimplexLogic or RepeaterLogic is included automatically in `LinkToReflector`.

## Multi-Port Topology

A multi-port installation may contain:

* Independent radio ports.
* A local link joining two or more radio ports.
* One reflector link joining selected radio ports to ReflectorLogic.

Example:

```text
Port 1 ↔ Port 2 ↔ Reflector
Port 3 ↔ Port 4
Ports 5, 6, 7 and 8 independent
```

This topology requires one reflector link containing ports 1 and 2, and one local link containing ports 3 and 4.

Ports 5 to 8 are declared in `[GLOBAL]/LOGICS` but are not included in either link.

All radio ports connected through one ReflectorLogic share that reflector connection and its selected talkgroup state.

## Strict Link Isolation

A radio logic may belong to no more than one link section.

This is a strict rule with no exceptions.

The following topology is prohibited:

```text
Reflector link:
RepeaterLogic1 ↔ SimplexLogic1 ↔ ReflectorLogic

Local link:
SimplexLogic1 ↔ RepeaterLogic2
```

SimplexLogic1 appears in both links. When both links are active, it indirectly connects RepeaterLogic2 to ReflectorLogic and merges the two intended groups.

The configuration workflow must detect and reject this overlap before building `svxlink.conf`.

A port already assigned to one link must be removed from that link before it can be assigned to another.

## Link Validation

Before configuration is built:

* Every enabled radio port must have a corresponding logic declaration.
* Every link member must refer to an enabled radio port or ReflectorLogic.
* A local link must contain at least two radio logics.
* A reflector link must contain at least one radio logic and ReflectorLogic.
* ReflectorLogic may appear only in the reflector link.
* No radio logic may appear in more than one link.
* An unlinked radio logic remains independently operational.
* Every radio logic in the reflector link must include the required `:9` DTMF control suffix.

The final configuration review must show each port as one of:

* Connected to the reflector.
* Connected through a named local link.
* Independent.
## Primary Installation Identity

Every multi-port installation must have exactly one primary port.

The callsign configured for that primary port is the primary callsign of the installation. Port ordering must not determine the installation identity once a primary port has been selected.

The primary callsign is used wherever one callsign must represent the installation as a whole, including:

* `ReflectorLogic`
* Node information
* Dashboard installation identification
* The system login display or MOTD

A single-port installation automatically uses the callsign of its only configured radio logic.

When reflector operation is enabled:

* The primary port must be included in the reflector link.
* `ReflectorLogic` uses the primary installation callsign.
* Additional ports may be included in the same reflector link.
* Additional ports may use the same callsign or different callsigns.
* A secondary-port callsign must never replace the selected primary installation callsign merely because of its port number or configuration order.

For example:

```text
Port 1 — RepeaterLogic — AK6BL — Primary
Port 2 — SimplexLogic — KO6IL-L
```

Both ports may be connected to the reflector:

```ini
[LinkToReflector]
CONNECT_LOGICS=RepeaterLogic1:9,SimplexLogic2:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

The reflector identity remains:

```ini
[ReflectorLogic]
CALLSIGN=AK6BL
```

For Protocol 3 operation, the `ReflectorLogic` callsign determines the X.509 client certificate identity. Deliberately changing the primary installation callsign may therefore require a new certificate request and approval by the reflector administrator.

When reflector operation is disabled, the primary port may remain independent or participate in a local link. It still provides the primary callsign for the installation.

## Installation-Wide Tone Settings

Courtesy, idle and closedown tones are installation-wide settings.

They must not be offered as independent per-port settings because the sounds are produced through shared SvxLink event-handling files.

The installation provides one selection for each of the following:

* Courtesy tone
* Courtesy beep frequency
* Repeater idle tone
* Repeater closedown tone

The selected courtesy behaviour applies through the shared `Logic.tcl` event handling.

The selected idle and closedown behaviour applies through the shared `RepeaterLogicType.tcl` event handling to every configured repeater logic.

Valid courtesy choices are:

* None
* Beep
* Morse T
* Morse K

Valid idle-tone choices are:

* None
* Pip
* Chime

Valid closedown-tone choices are:

* None
* Biboop
* VA

`None` is a valid deliberate selection in every case.

A courtesy tone is normally recommended for repeater operation, but it is not mandatory and the dashboard must not prevent the operator from selecting None.

The configuration workflow must apply each shared event-file modification once, regardless of the number of configured radio ports.

## Configuration Sequence

The configuration workflow must establish the available hardware, configure every enabled radio port and identify the primary installation port before reflector or link topology is configured.

The sequence is:

1. Select the hardware platform.
2. Select and enable the required radio ports.
3. Assign each enabled port as `SimplexLogic` or `RepeaterLogic`.
4. Complete the node, interface, squelch, identification and CW configuration for every enabled port.
5. Configure the installation-wide courtesy, idle and closedown tones.
6. Complete any repeater-specific operating settings.
7. Select the primary installation port. A single-port installation selects its only port automatically.
8. Select whether a reflector will be used.
9. Configure the reflector protocol and authentication method when required.
10. Define the port-link topology.
11. Validate the complete configuration.
12. Review and build the SvxLink configuration.

The primary installation port is selected only after the configured port callsigns and logic types are available for review.

Reflector selection follows primary installation identity so that the correct callsign is applied to `ReflectorLogic` and, for Protocol 3 operation, to the X.509 certificate request.

Link topology is deliberately the final configuration-parameter stage. This ensures that the enabled ports, their logic types, the primary installation identity and the selected reflector route are all known before any connections are created.


### Reflector Selection

Before link topology is configured, the user must select one of the following reflector routes:

* No reflector
* Federation Family Protocol 2 reflector
* Other Protocol 2 reflector
* Protocol 3 reflector using X.509 certification

Selecting **No reflector** allows the system to contain independent radio ports and local links between radio ports.

A Federation Family reflector uses the supplied network settings and requires the network-specific 16-character password.

Other Protocol 2 reflectors require the hostname or IP address, port number, callsign, and password supplied by the reflector administrator. The Federation Family 16-character password requirement must not be imposed on these reflectors.

Protocol 3 reflectors require the hostname or IP address, port number, callsign, certificate subject information, and the X.509 certificate request and approval process.

### Single-Port Topology

A single-port system does not require a separate topology-selection page.

If reflector operation is disabled, the configured radio logic remains independent.

If reflector operation is enabled, the configured radio logic is automatically linked to `ReflectorLogic`.

Example:

```ini
[ReflectorLink]
CONNECT_LOGICS=SimplexLogic:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

The `:9` suffix is required on each radio logic connected to `ReflectorLogic` so that DTMF talkgroup commands can be passed to the reflector.

### Multi-Port Topology

In a multi-port system, every enabled port must be assigned explicitly to one of the following:

* Independent operation
* A named local link
* The reflector link

Local links may contain two or more radio ports.

Examples include:

* Port 1 linked to Port 2
* Port 3 linked to Port 4
* Ports 1, 2, and 4 linked together
* Ports 1 and 2 linked to the reflector while Ports 3 and 4 form a separate local link

Example reflector link:

```ini
[ReflectorLink]
CONNECT_LOGICS=RepeaterLogic2:9,SimplexLogic3:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

Example local link:

```ini
[LocalLink1]
CONNECT_LOGICS=SimplexLogic1,RepeaterLogic2
DEFAULT_ACTIVE=1
TIMEOUT=300
```

The user is responsible for defining the required local connectivity. The dashboard must validate the selected topology before allowing the configuration to be built.

### Strict Port Membership Rule

Each radio port or radio logic may belong to no more than one link.

This rule has no exceptions.

The following overlapping topology is invalid:

```ini
[ReflectorLink]
CONNECT_LOGICS=RepeaterLogic1:9,SimplexLogic1:9,ReflectorLogic

[LocalLink1]
CONNECT_LOGICS=SimplexLogic1,RepeaterLogic2
```

`SimplexLogic1` appears in both links and would create an overlapping path.

The dashboard must reject this configuration and identify the port already assigned to another link.

### Incomplete Port Handling

Because topology selection occurs after port configuration, every enabled port should normally be complete before it is offered for linking.

If an incomplete port is encountered because of an interrupted setup, imported configuration, or later reconfiguration, the dashboard must:

1. Identify the missing configuration.
2. Preserve the pending link selection.
3. Take the user directly to the first incomplete configuration stage for that port.
4. Return the user to the topology page when the port configuration is complete.

The configuration must not be built while any selected port remains incomplete.

### Disabled Port Handling

A port that was not enabled during hardware selection cannot be assigned to a link.

If the user requires an additional port, the dashboard must return to the hardware-port selection stage so that the port can be enabled and prepared correctly.

The topology page must not automatically enable hardware ports because additional hardware preparation, overlays, audio devices, and interface settings may be required.

### Topology Validation

Before continuing, the dashboard must confirm that:

* Every enabled port has a completed logic configuration.
* Every enabled port has an explicit topology assignment.
* Every local link contains at least two radio ports.
* A reflector link contains at least one radio port and `ReflectorLogic`.
* No radio port appears in more than one link.
* `ReflectorLogic` appears only in the reflector link.
* Every radio logic connected to `ReflectorLogic` includes the required `:9` suffix.
* A reflector link cannot be created when reflector operation is disabled.
* Only one `ReflectorLogic` and one reflector destination are configured.

Support for simultaneous connections to multiple reflectors is outside the present scope.

### Completion Route

During initial setup, a valid topology continues to the final review page. The review must show every enabled port, its logic type, and its link assignment before the configuration is built.

When topology is changed through the dashboard reconfiguration menu, a valid saved configuration must return directly to the build page, preserving the established V3.2 reconfiguration behaviour.

## Current Scope

The supported topology contains no more than one ReflectorLogic and one reflector connection.

Different local port groups may be configured on a case-by-case basis, subject to the strict isolation rule.

Connecting different ports to multiple independent reflectors is outside the current scope.

## User-Defined Local Links

Multi-port local links are defined by the operator according to the requirements of the individual installation.

The configuration workflow will provide an example based on the standard SvxLink link structure:

```ini
[LinkToR4]
CONNECT_LOGICS=RepeaterLogic1:94:SK3AB,SimplexLogic2:92:SK3CD
#DEFAULT_ACTIVE=1
TIMEOUT=300
#ACTIVATE_ON_ACTIVITY=RepeaterLogic1
#ACTIVATE_ON_TG=SimplexLogic2:240.*
```

The operator may define:

* The link section name.
* The available radio ports participating in the link.
* The DTMF command assigned to each participating logic.
* The identification or announcement label associated with each logic.
* Whether the link is active by default.
* The link timeout.
* Any supported activity or talkgroup activation conditions.

The configuration workflow generates the appropriate SimplexLogic or RepeaterLogic section names from the selected ports.

The operator remains responsible for deciding the intended operational connectivity of each local link.

The configuration workflow remains responsible for:

* Rejecting references to ports that are not enabled.
* Rejecting duplicate or invalid link section names.
* Rejecting a link containing fewer than two radio logics.
* Preventing a radio port from belonging to more than one link.
* Preventing a port assigned to the reflector link from also belonging to a local link.
* Presenting the resulting topology for review before configuration is built.

A local link may subsequently be replaced or reconfigured through the dashboard reconfiguration menu.

## Reconfiguration Behaviour

The initial configuration workflow and dashboard reconfiguration workflow follow different return paths.

During initial setup, the operator progresses through the complete sequence:

```text
Configure local node or ports
→ Configure link topology and reflector access
→ Review complete configuration
→ Build and deploy
```

When an existing setting is opened through the dashboard reconfiguration menu, saving that setting must return directly to the Build page.

The operator must not be sent through the remaining initial-setup pages.

This preserves the established SvxLink-Dash-V3.2 reconfiguration behaviour:

```text
Dashboard
→ Reconfiguration menu
→ Selected configuration page
→ Build
→ Deploy updated configuration
```

This direct return applies to changes involving:

* Local link topology.
* Reflector selection.
* Reflector authentication.
* Ports participating in the reflector link.
* Other existing configuration pages opened through reconfiguration.

The Build page remains the common point at which the revised model is rendered, reviewed and deployed.

---

# Reflector Protocol Notice

SvxLink-Dash-V3.2 was written primarily for the following SvxReflector Protocol 2 networks running SvxLink Version 26.05.1:

* UKWide
* North America
* Australia

Other SvxReflectors may also be configured. Before beginning reflector setup, the operator must confirm the authentication method required by the destination reflector manager:

* Callsign and password authentication using SvxReflector Protocol 2.
* X.509 certificate authentication using SvxReflector Protocol 3.

For Protocol 2, the operator must obtain the required connection address, port and password from the reflector manager.

For Protocol 3, the configuration workflow will collect the information required to generate the appropriate `[ReflectorLogic]` certificate settings. SvxLink then manages creation of the private key and Certificate Signing Request, submission of the request to the reflector, and retrieval of the signed client certificate after approval by the reflector manager.

Successful Protocol 3 access depends on the destination reflector having a correctly configured certificate chain, CA bundle and server identity.

## Reflector Selection Routes

Reflector configuration provides four distinct routes.

### No Reflector

The installation operates locally without ReflectorLogic.

For a multi-port installation, local port-to-port links may still be configured.

### Federation Family Reflector

The Federation Family currently comprises:

* UKWide
* North America
* Australia
* YorkshireNet

The selected reflector supplies predefined connection details, including its name, hostname, port, website and suggested monitoring talkgroups.

The operator must enter the 16-character password issued by the selected reflector.

Federation Family access uses SvxReflector Protocol 2 callsign-and-password authentication.

The password must contain exactly 16 characters.

### Other Protocol 2 Reflector

The operator must obtain the following information from the destination reflector manager:

* Reflector name.
* Hostname or IP address.
* Port number.
* Authentication password.
* Any recommended default or monitoring talkgroups.

The password is passed to SvxLink as the ReflectorLogic `AUTH_KEY`.

The dashboard must not impose the Federation Family 16-character password rule on an independent Protocol 2 reflector. It must accept the password supplied by that reflector’s manager.

### Protocol 3 Reflector

The operator must obtain the following information from the destination reflector manager:

* Reflector name.
* Hostname or IP address.
* Port number.
* Any required certificate identity information.
* Any recommended default or monitoring talkgroups.

Protocol 3 uses X.509 certificate authentication rather than a shared reflector password.

SvxLink generates the client private key and Certificate Signing Request, downloads the reflector CA bundle, and submits the request to the reflector.

The reflector manager must inspect and approve the pending request before the node receives its signed client certificate and completes authentication.

Successful access depends on the destination reflector having:

* A valid root, issuing and server certificate chain.
* A CA bundle containing the active root certificate.
* A server certificate covering the supplied hostname or IP address.
* A working process for reviewing and signing pending client requests.

The client cannot repair or bypass an incorrectly configured reflector certificate system.

## Common Reflector Information

The node callsign is taken from the configured radio installation and must not be entered again unless a separate reflector identity is explicitly required.

Standard certificate paths, filenames and safe connection defaults are generated automatically and are not presented as routine questions.

Default and monitoring talkgroups remain specific to the selected reflector and installation.

For multi-port installations, reflector access is configured after all ports have been defined. The operator then selects which available ports participate in the single reflector link.

Each participating radio logic is added to `CONNECT_LOGICS` with the required `:9` DTMF control suffix.

A port assigned to the reflector link cannot belong to any local port-to-port link.

# Current Limitations

Currently not implemented:

- Browser audio streaming

This may be added in future versions.

---

# Credits

SvxLink Software: Version 26.05.1

Tobias Blömberg SM0SVX

Version 3.2

was developed by Chris Jackson, G4NAB.
Additional assistance with Python, Flask, configuration rendering,
debugging and documentation was provided through ChatGPT by OpenAI.

---

# License

This project is distributed as useful to the amateur radio community.
