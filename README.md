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

## Configuration Sequence

Link topology is configured only after all single-port or multi-port radio logics have been defined.

The intended workflow is:

```text
Configure local node or ports
→ Configure link topology and reflector access
→ Review complete configuration
→ Build and deploy
```

## Current Scope

The supported topology contains no more than one ReflectorLogic and one reflector connection.

Different local port groups may be configured on a case-by-case basis, subject to the strict isolation rule.

Connecting different ports to multiple independent reflectors is outside the current scope.

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
