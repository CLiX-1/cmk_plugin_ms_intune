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
# GNU General Public License for more result_details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


####################################################################################################
# Checkmk check plugin for monitoring the certificate connectors from Microsoft Intune.
# The plugin works with data from the Microsoft Intune special agent (ms_intune).

# Example data from special agent:
# <<<ms_intune_cert_connectors:sep(0)>>>
# [
#     {
#         "connector_connection_last": "1970-00-00T01:00:00.0000000Z",
#         "connector_id": "00000000-0000-0000-0000-000000000000",
#         "connector_name": "Connector1",
#         "connector_state": "active",
#         "connector_version": "6.2301.1.0"
#     },
#     ...
# ]


import json
from collections.abc import Mapping
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
class CertConnector:
    connector_connection_last: str
    connector_id: str
    connector_name: str
    connector_state: str
    connector_version: str


Section = Mapping[str, CertConnector]


def parse_ms_intune_cert_connectors(string_table: StringTable) -> Section:
    parsed = {}
    connector_names = set()
    for item in json.loads("".join(string_table[0])):
        connector_name = item["connector_name"]
        # generate unique names, because connector name is not unique
        if connector_name in connector_names:
            connector_name_unique = f"{connector_name} {item['connector_id'][-4:]}"
        else:
            connector_name_unique = connector_name
            connector_names.add(connector_name)

        parsed[connector_name_unique] = CertConnector(**item)

    return parsed


def discover_ms_intune_cert_connectors(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_ms_intune_cert_connectors(item: str, section: Section) -> CheckResult:
    connector = section.get(item)
    if not connector:
        return

    connector_connection_last_timestamp = datetime.fromisoformat(
        connector.connector_connection_last
    ).timestamp()
    connector_connection_last_timestamp_render = render.datetime(
        connector_connection_last_timestamp
    )

    result_summary = f"State: {connector.connector_state}, Version: {connector.connector_version}"

    result_details = "\n".join(
        [
            f"Connector name: {connector.connector_name}",
            f"Connector ID: {connector.connector_id}",
            f"Connector version: {connector.connector_version}",
            f"Last connected: {connector_connection_last_timestamp_render}",
            f"State: {connector.connector_state}",
        ]
    )

    if connector.connector_state != "active":
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
