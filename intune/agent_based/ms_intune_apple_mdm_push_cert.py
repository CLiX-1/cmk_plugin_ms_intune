#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

# Copyright (C) 2024, 2025  Christopher Pommer <cp.software@outlook.de>

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


####################################################################################################
# Checkmk check plugin for monitoring the Apple MDM push certificate from Microsoft Intune.
# The plugin works with data from the Microsoft Intune special agent (ms_intune).

# Example data from special agent:
# <<<ms_intune_apple_mdm_push_cert:sep(0)>>>
# {
#     "cert_appleid": "mail@domain.de",
#     "cert_expiration": "1970-00-00T01:00:00Z"
# }


import json
from collections.abc import Mapping
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
    Metric,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class ApplePushCert:
    cert_appleid: str
    cert_expiration: str


Section = ApplePushCert


def parse_ms_intune_apple_mdm_push_cert(string_table: StringTable) -> Section:
    parsed = json.loads(string_table[0][0])
    return ApplePushCert(**parsed)


def discover_ms_intune_apple_mdm_push_cert(section: Section) -> DiscoveryResult:
    yield Service()


def check_ms_intune_apple_mdm_push_cert(params: Mapping[str, Any], section: Section) -> CheckResult:
    cert = section
    if not cert:
        return

    params_levels_cert_expiration = params.get("cert_expiration")

    cert_expiration_timestamp = datetime.fromisoformat(cert.cert_expiration).timestamp()
    cert_expiration_timestamp_render = render.datetime(cert_expiration_timestamp)

    cert_expiration_timespan = cert_expiration_timestamp - datetime.now().timestamp()

    if cert_expiration_timespan > 0:
        yield from check_levels(
            cert_expiration_timespan,
            levels_lower=(params_levels_cert_expiration),
            metric_name="ms_intune_apple_mdm_push_cert_remaining_validity",
            label="Remaining",
            render_func=render.timespan,
        )
    else:
        yield from check_levels(
            cert_expiration_timespan,
            levels_lower=(params_levels_cert_expiration),
            label="Expired",
            render_func=lambda x: f"{render.timespan(abs(x))} ago",
        )

        # To prevent a negative value for the metric.
        yield Metric(
            name="ms_intune_apple_mdm_push_cert_remaining_validity",
            value=0.0,
            levels=params_levels_cert_expiration[1],
        )

    yield Result(
        state=State.OK,
        summary=f"Expiration time: {cert_expiration_timestamp_render}",
        details=(
            f"Expiration time: {cert_expiration_timestamp_render}\n"
            f"Apple ID: {cert.cert_appleid}"
        ),
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
