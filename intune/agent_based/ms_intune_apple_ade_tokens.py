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
# Checkmk check plugin for monitoring thec Apple Automated Device Enrollment (ADE) tokens from
# Microsoft Intune. The plugin works with data from the Microsoft Intune special agent (ms_intune).

# Example data from special agent:
# <<<ms_intune_apple_ade_tokens:sep(0)>>>
# [
#     {
#         "token_appleid": "ade@domain.td",
#         "token_expiration": "1970-00-00T01:00:00Z",
#         "token_id": "00000000-0000-0000-0000-000000000000",
#         "token_name": "Apple Business Manager",
#         "token_type": "dep"
#     },
#     ...
# ]


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
    Metric,
    render,
    Result,
    Service,
    State,
    StringTable,
)


@dataclass(frozen=True)
class AdeToken:
    token_appleid: str
    token_expiration: str
    token_id: str
    token_name: str
    token_type: str


Section = Mapping[str, AdeToken]


def parse_ms_intune_apple_ade_tokens(string_table: StringTable) -> Section:
    parsed = {}
    token_names = set()
    for item in json.loads("".join(string_table[0])):
        token_name = item["token_name"]
        # generate unique names, because token name is not unique
        if token_name in token_names:
            token_name_unique = f"{token_name} {item['token_id'][-4:]}"
        else:
            token_name_unique = token_name
            token_names.add(token_name)

        parsed[token_name_unique] = AdeToken(**item)

    return parsed


def discover_ms_intune_apple_ade_tokens(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_ms_intune_apple_ade_tokens(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    token = section.get(item)
    if not token:
        return

    params_levels_token_expiration = params.get("token_expiration")

    token_expiration_timestamp = datetime.fromisoformat(token.token_expiration).timestamp()
    token_expiration_timestamp_render = render.datetime(token_expiration_timestamp)

    token_expiration_timespan = token_expiration_timestamp - datetime.now().timestamp()

    result_details = "\n".join(
        [
            f"Expiration time: {token_expiration_timestamp_render}",
            f"Token name: {token.token_name}",
            f"Token ID: {token.token_id}",
            f"Token type: {token.token_type}",
            f"Apple ID: {token.token_appleid}",
        ]
    )

    if token_expiration_timespan > 0:
        yield from check_levels(
            token_expiration_timespan,
            levels_lower=(params_levels_token_expiration),
            metric_name="ms_intune_apple_ade_tokens_remaining_validity",
            label="Remaining",
            render_func=render.timespan,
        )
    else:
        yield from check_levels(
            token_expiration_timespan,
            levels_lower=(params_levels_token_expiration),
            label="Expired",
            render_func=lambda x: f"{render.timespan(abs(x))} ago",
        )

        # To prevent a negative value for the metric.
        yield Metric(
            name="ms_intune_apple_ade_tokens_remaining_validity",
            value=0.0,
            levels=params_levels_token_expiration[1],
        )

    yield Result(
        state=State.OK,
        summary=f"Expiration time: {token_expiration_timestamp_render}",
        details=result_details,
    )


agent_section_ms_intune_apple_ade_tokens = AgentSection(
    name="ms_intune_apple_ade_tokens",
    parse_function=parse_ms_intune_apple_ade_tokens,
)


check_plugin_ms_intune_apple_ade_tokens = CheckPlugin(
    name="ms_intune_apple_ade_tokens",
    service_name="Intune Apple ADE token %s",
    discovery_function=discover_ms_intune_apple_ade_tokens,
    check_function=check_ms_intune_apple_ade_tokens,
    check_ruleset_name="ms_intune_apple_ade_tokens",
    check_default_parameters={"token_expiration": ("fixed", (1209600.0, 432000.0))},
)
