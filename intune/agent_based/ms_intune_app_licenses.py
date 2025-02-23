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
# Checkmk check plugin for monitoring the app licenses from Microsoft Intune.
# The plugin works with data from the Microsoft Intune special agent (ms_intune).

# Example data from special agent:
# <<<ms_intune_app_licenses:sep(0)>>>
# [
#     {
#         "app_type": "iOS VPP"
#         "app_name": "Adobe Account Access",
#         "app_publisher": "ADOBE SYSTEMS SOFTWARE IRELAND LIMITED",
#         "app_license_total": 40,
#         "app_license_consumed": 7
#         "app_assigned": true
#     },
#     {
#         "app_type": "MS Store for business"
#         "app_name": "Microsoft Outlook",
#         "app_publisher": "Microsoft Corporation",
#         "app_license_total": 100,
#         "app_license_consumed": 92
#         "app_assigned": true
#     },
#     ...
# ]


import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
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
class IntuneApp:
    app_type: str
    app_name: str
    app_publisher: str
    app_license_total: int
    app_license_consumed: int
    app_assigned: bool


Section = Mapping[str, IntuneApp]


def parse_ms_intune_app_licenses(string_table: StringTable) -> Section:
    parsed = {}
    for item in json.loads("".join(string_table[0])):
        service_name = f"{item['app_name']} - {item['app_type']}"
        parsed[service_name] = IntuneApp(**item)
    return parsed


def discover_ms_intune_app_licenses(section: Section) -> DiscoveryResult:
    for group in section:
        yield Service(item=group)


def check_ms_intune_app_licenses(
    item: str, params: Mapping[str, Any], section: Section
) -> CheckResult:
    license = section.get(item)
    if not license:
        return

    app_license_consumed_pct = round(
        license.app_license_consumed / license.app_license_total * 100, 2
    )
    lic_units_available = license.app_license_total - license.app_license_consumed

    result_level = ""
    result_state = State.OK
    levels_consumed_abs = (None, None)
    levels_consumed_pct = (None, None)
    params_lic_total_min = params["lic_total_min"]
    if license.app_license_total >= params_lic_total_min:
        params_levels_available = params["lic_unit_available_lower"]
        if params_levels_available[1][1]:
            warning_level, critical_level = params_levels_available[1][1]

            if params_levels_available[0] == "lic_unit_available_lower_pct":
                levels_consumed_pct = (100 - warning_level, 100 - critical_level)

                available_percent = lic_units_available / license.app_license_total * 100

                if available_percent < critical_level:
                    result_state = State.CRIT
                elif available_percent < warning_level:
                    result_state = State.WARN

                result_level = (
                    f" (warn/crit below {render.percent(warning_level)}/"
                    f"{render.percent(critical_level)} available)"
                )

            else:
                levels_consumed_abs = (
                    license.app_license_total - warning_level,
                    license.app_license_total - critical_level,
                )

                if license.app_license_consumed > levels_consumed_abs[1]:
                    result_state = State.CRIT
                elif license.app_license_consumed > levels_consumed_abs[0]:
                    result_state = State.WARN

                result_level = f" (warn/crit below {warning_level}/{critical_level} available)"

    result_summary = (
        f"Consumed: {render.percent(app_license_consumed_pct)} - "
        f"{license.app_license_consumed} of {license.app_license_total}"
        f", Available: {lic_units_available}"
        f"{result_level}"
    )

    result_details = "\n".join(
        [
            f"Name: {license.app_name}",
            f"Publisher: {license.app_publisher}",
            f"Type: {license.app_type}",
            f"Total: {license.app_license_total}",
            f"Used: {license.app_license_consumed}",
            f"Is assigned: {'yes' if license.app_assigned else 'no'}",
        ]
    )

    yield Result(
        state=result_state,
        summary=result_summary,
        details=result_details,
    )

    yield Metric(name="ms_intune_app_licenses_total", value=license.app_license_total)
    yield Metric(
        name="ms_intune_app_licenses_consumed",
        value=license.app_license_consumed,
        levels=levels_consumed_abs,
    )
    yield Metric(
        name="ms_intune_app_licenses_consumed_pct",
        value=app_license_consumed_pct,
        levels=levels_consumed_pct,
    )
    yield Metric(name="ms_intune_app_licenses_available", value=lic_units_available)


agent_section_ms_intune_app_licenses = AgentSection(
    name="ms_intune_app_licenses",
    parse_function=parse_ms_intune_app_licenses,
)


check_plugin_ms_intune_app_licenses = CheckPlugin(
    name="ms_intune_app_licenses",
    service_name="Intune app %s",
    discovery_function=discover_ms_intune_app_licenses,
    check_function=check_ms_intune_app_licenses,
    check_ruleset_name="ms_intune_app_licenses",
    check_default_parameters={
        "lic_unit_available_lower": ("lic_unit_available_lower_pct", ("fixed", (10.0, 5.0))),
        "lic_total_min": 1,
    },
)
