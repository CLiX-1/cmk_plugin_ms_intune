#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# Copyright (C) 2024  Christopher Pommer <cp.software@outlook.de>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class CertInfo:
    cert_appleid: str
    cert_expiration: str


Section = Sequence[CertInfo]

# Example data from special agent:
# <<<ms_intune_apple_mdm_push_cert:sep(0)>>>
# {
#     "cert_appleid": "mail@domain.de",
#     "cert_expiration": "2000-01-01T00:00:00Z"
# }


def parse_ms_intune_apple_mdm_push_cert(string_table: StringTable) -> Section:
    parsed = json.loads(string_table[0][0])
    return parsed


def discover_ms_intune_apple_mdm_push_cert(section: Section) -> DiscoveryResult:
    yield Service()


def check_ms_intune_apple_mdm_push_cert(params: Mapping[str, Any], section: Section) -> CheckResult:
    cert_appleid = section["cert_appleid"]
    cert_expiration = section["cert_expiration"]

    params_levels_cert_expiration = params.get("cert_expiration")

    cert_expiration_datetime = datetime.strptime(cert_expiration, "%Y-%m-%dT%H:%M:%SZ")
    cert_expiration_timestamp = cert_expiration_datetime.timestamp()
    cert_expiration_timestamp_render = render.datetime(int(cert_expiration_timestamp))

    cert_expiration_timespan = cert_expiration_timestamp - datetime.now().timestamp()

    if cert_expiration_timespan > 0:
        yield from check_levels(
            cert_expiration_timespan,
            levels_lower=(params_levels_cert_expiration),
            label="Remaining",
            render_func=render.timespan,
        )
    else:
        yield from check_levels(
            cert_expiration_timespan,
            levels_lower=(params_levels_cert_expiration),
            label="Expired",
            render_func=lambda x: "%s ago" % render.timespan(abs(x)),
        )

    yield Result(
        state=State.OK,
        summary=f"Expiration time: {cert_expiration_timestamp_render} (UTC)",
        details=f"Expiration time: {cert_expiration_timestamp_render} (UTC)\\n Apple ID: {cert_appleid}",
    )


agent_section_ms_intune_apple_push_cert = AgentSection(
    name="ms_intune_apple_mdm_push_cert",
    parse_function=parse_ms_intune_apple_mdm_push_cert,
)


check_plugin_ms_intune_apple_mdm_push_cert = CheckPlugin(
    name="ms_intune_apple_mdm_push_cert",
    service_name="Intune Apple MDM push certificate",
    discovery_function=discover_ms_intune_apple_mdm_push_cert,
    check_function=check_ms_intune_apple_mdm_push_cert,
    check_ruleset_name="ms_intune_apple_mdm_push_cert",
    check_default_parameters={"cert_expiration": ("fixed", (1209600.0, 432000.0))},
)
