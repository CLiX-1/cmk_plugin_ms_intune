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
class TokenInfo:
    token_id: str
    token_appleid: str
    token_state: str
    token_expiration: str


# Example data from special agent:
# <<<ms_intune_apple_vpp_tokens:sep(0)>>>
# [
#     {
#         "token_id": "00000000-0000-0000-0000-000000000000",
#         "token_appleid": "vpp@domain.td",
#         "token_state": "valid",
#         "token_expiration": "2025-03-02T06:54:05Z"
#     },
#     {
#         "token_id": "00000000-0000-0000-0000-000000000001",
#         "token_appleid": "vpp@domain.td",
#         "token_state": "valid",
#         "token_expiration": "2025-03-02T06:54:05Z"
#     },
#     ...
# ]

Section = Mapping[str, Sequence[TokenInfo]]


def parse_ms_intune_apple_vpp_tokens(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        parsed[item["token_id"]] = item
    return parsed


def discover_ms_intune_apple_vpp_tokens(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_ms_intune_apple_vpp_tokens(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    token = section.get(item)
    if not token:
        return

    params_levels_token_expiration = params.get("token_expiration")

    token_appleid = token["token_appleid"]
    token_state = token["token_state"]
    token_expiration = token["token_expiration"]

    token_expiration_datetime = datetime.strptime(token_expiration, "%Y-%m-%dT%H:%M:%SZ")
    token_expiration_timestamp = token_expiration_datetime.timestamp()
    token_expiration_timestamp_render = render.datetime(int(token_expiration_timestamp))

    token_expiration_timespan = token_expiration_timestamp - datetime.now().timestamp()

    result_details = (
        f"Expiration time: {token_expiration_timestamp_render} (UTC)"
        f"\\nState: {token_state}"
        f"\\nApple ID: {token_appleid}"
    )
    result_summary = f"Expiration time: {token_expiration_timestamp_render} (UTC), State: {token_state}"

    if token_expiration_timespan > 0:
        yield from check_levels(
            token_expiration_timespan,
            levels_lower=(params_levels_token_expiration),
            label="Remaining",
            render_func=render.timespan,
        )
    else:
        yield from check_levels(
            token_expiration_timespan,
            levels_lower=(params_levels_token_expiration),
            label="Expired",
            render_func=lambda x: "%s ago" % render.timespan(abs(x)),
        )

    if token_state != "valid":
        yield Result(
            state=State.CRIT,
            summary=result_summary,
            details=result_details,
        )
    else:
        yield Result(
            state=State.OK,
            summary=result_summary,
            details=result_details,
        )


agent_section_ms_intune_apple_vpp_tokens = AgentSection(
    name="ms_intune_apple_vpp_tokens",
    parse_function=parse_ms_intune_apple_vpp_tokens,
)


check_plugin_ms_intune_apple_vpp_tokens = CheckPlugin(
    name="ms_intune_apple_vpp_tokens",
    service_name="Intune VPP token %s",
    discovery_function=discover_ms_intune_apple_vpp_tokens,
    check_function=check_ms_intune_apple_vpp_tokens,
    check_ruleset_name="ms_intune_apple_vpp_tokens",
    check_default_parameters={"token_expiration": ("fixed", (1209600.0, 432000.0))},
)
