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
# The graph parameters are part of the Microsoft Intune special agent (ms_intune).


from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import (
    Color,
    CriticalOf,
    DecimalNotation,
    Metric,
    StrictPrecision,
    TimeNotation,
    Unit,
    WarningOf,
)
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

UNIT_COUNTER = Unit(DecimalNotation(""), StrictPrecision(0))
UNIT_PERCENTAGE = Unit(DecimalNotation("%"))
UNIT_TIME = Unit(TimeNotation())


# Microsoft Intune App Licenses

metric_ms_intune_app_licenses_consumed = Metric(
    name="ms_intune_app_licenses_consumed",
    title=Title("Consumed"),
    unit=UNIT_COUNTER,
    color=Color.CYAN,
)

metric_ms_intune_app_licenses_consumed_pct = Metric(
    name="ms_intune_app_licenses_consumed_pct",
    title=Title("Usage"),
    unit=UNIT_PERCENTAGE,
    color=Color.BLUE,
)

metric_ms_intune_app_licenses_total = Metric(
    name="ms_intune_app_licenses_total",
    title=Title("Total"),
    unit=UNIT_COUNTER,
    color=Color.DARK_CYAN,
)

metric_ms_intune_app_licenses_available = Metric(
    name="ms_intune_app_licenses_available",
    title=Title("Available"),
    unit=UNIT_COUNTER,
    color=Color.LIGHT_GRAY,
)


graph_ms_intune_app_licenses_count = Graph(
    name="ms_intune_app_licenses_count",
    title=Title("License count"),
    compound_lines=[
        "ms_intune_app_licenses_consumed",
        "ms_intune_app_licenses_available",
    ],
    simple_lines=[
        "ms_intune_app_licenses_total",
        WarningOf("ms_intune_app_licenses_consumed"),
        CriticalOf("ms_intune_app_licenses_consumed"),
    ],
)

graph_ms_intune_app_licenses_usage = Graph(
    name="ms_intune_app_licenses_usage",
    title=Title("License usage"),
    minimal_range=MinimalRange(0, 100),
    simple_lines=[
        "ms_intune_app_licenses_consumed_pct",
        WarningOf("ms_intune_app_licenses_consumed_pct"),
        CriticalOf("ms_intune_app_licenses_consumed_pct"),
    ],
)

perfometer_ms_intune_app_licenses_consumed_pct = Perfometer(
    name="ms_intune_app_licenses_consumed_pct",
    focus_range=FocusRange(Closed(0), Closed(100)),
    segments=["ms_intune_app_licenses_consumed_pct"],
)


# Microsoft Intune Apple ADE tokens

metric_ms_intune_apple_ade_tokens_remaining_validity = Metric(
    name="ms_intune_apple_ade_tokens_remaining_validity",
    title=Title("Remaining token validity time"),
    unit=UNIT_TIME,
    color=Color.YELLOW,
)

perfometer_ms_intune_apple_ade_tokens_remaining_validity = Perfometer(
    name="ms_intune_apple_ade_tokens_remaining_validity",
    focus_range=FocusRange(Closed(0), Open(15552000)),
    segments=["ms_intune_apple_ade_tokens_remaining_validity"],
)


# Microsoft Intune Apple MDM Push Certificate

metric_ms_intune_apple_mdm_push_cert_remaining_validity = Metric(
    name="ms_intune_apple_mdm_push_cert_remaining_validity",
    title=Title("Remaining certificate validity time"),
    unit=UNIT_TIME,
    color=Color.YELLOW,
)

perfometer_ms_intune_apple_mdm_push_cert_remaining_validity = Perfometer(
    name="ms_intune_apple_mdm_push_cert_remaining_validity",
    focus_range=FocusRange(Closed(0), Open(15552000)),
    segments=["ms_intune_apple_mdm_push_cert_remaining_validity"],
)


# Microsoft Intune Apple VPP Tokens

metric_ms_intune_apple_vpp_tokens_remaining_validity = Metric(
    name="ms_intune_apple_vpp_tokens_remaining_validity",
    title=Title("Remaining token validity time"),
    unit=UNIT_TIME,
    color=Color.YELLOW,
)

perfometer_ms_intune_apple_vpp_tokens_remaining_validityy = Perfometer(
    name="ms_intune_apple_vpp_tokens_remaining_validity",
    focus_range=FocusRange(Closed(0), Open(15552000)),
    segments=["ms_intune_apple_vpp_tokens_remaining_validity"],
)
