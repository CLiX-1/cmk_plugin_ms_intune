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
# GNU General Public License for more result_details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from cmk.agent_based.v2 import (
    AgentSection,
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
class ConnectorInfo:
    connector_connection_last: str
    connector_state: str
    connector_name: str
    connector_version: str


Section = Mapping[str, Sequence[ConnectorInfo]]

# Example data from special agent:
# <<<ms_intune_cert_connectors:sep(0)>>>
# [
#     {
#         "connector_connection_last": "2024-05-18T21:33:26.1092739Z",
#         "connector_state": "active",
#         "connector_name": "Connector1",
#         "connector_version": "6.2301.1.0"
#     },
#     {
#         "connector_connection_last": "2024-05-18T21:29:30.5308288Z",
#         "connector_state": "active",
#         "connector_name": "Connector2",
#         "connector_version": "6.2301.1.0"
#     },
#     ...
# ]


def parse_ms_intune_cert_connectors(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        parsed[item["connector_name"]] = item
    return parsed


def discover_ms_intune_cert_connectors(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_ms_intune_cert_connectors(item: str, section: Section) -> CheckResult:
    connector = section.get(item)
    if not connector:
        return

    connector_connection_last = connector["connector_connection_last"]
    connector_state = connector["connector_state"]
    connector_version = connector["connector_version"]

    connector_connection_last_datetime = datetime.fromisoformat(connector_connection_last)
    connector_connection_last_timestamp = connector_connection_last_datetime.timestamp()
    connector_connection_last_timestamp_render = render.datetime(int(connector_connection_last_timestamp))

    result_summary = f"State: {connector_state}"

    result_details = (
        f"State: {connector_state}"
        f"\\nLast connected: {connector_connection_last_timestamp_render}"
        f"\\nConnector version: {connector_version}"
    )

    if connector_state != "active":
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


agent_section_ms_intune_cert_connectors = AgentSection(
    name="ms_intune_cert_connectors",
    parse_function=parse_ms_intune_cert_connectors,
)


check_plugin_ms_intune_cert_connectors = CheckPlugin(
    name="ms_intune_cert_connectors",
    service_name="Intune connector %s",
    discovery_function=discover_ms_intune_cert_connectors,
    check_function=check_ms_intune_cert_connectors,
)
