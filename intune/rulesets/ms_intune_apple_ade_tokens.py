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
# Checkmk ruleset to set the expiration time thresholds of Apple ADE tokens.
# This ruleset is part of the Microsoft Intune special agent (ms_intune).


from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.form_specs.validators import NumberInRange
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_ms_intune_apple_ade_tokens() -> Dictionary:
    return Dictionary(
        title=Title("Intune Apple ADE Tokens"),
        help_text=Help(
            "Parameters for the expiration time thresholds from Apple ADE tokens "
            "(Automated Device Enrollment) configured in Microsoft Intune. "
            "To use this service, you need to set up the <b>Microsoft Intune</b> special agent."
        ),
        elements={
            "token_expiration": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Token Expiration"),
                    help_text=Help(
                        "Specify the lower levels for the Apple ADE token expiration time. "
                        "The default values are 14 days (WARN) and 5 days (CRIT). "
                        "To ignore token expiration, select 'No levels'."
                    ),
                    form_spec_template=TimeSpan(
                        custom_validate=(NumberInRange(min_value=0),),
                        displayed_magnitudes=[
                            TimeMagnitude.DAY,
                        ],
                    ),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue(value=(1209600.0, 432000.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_ms_intune_apple_ade_tokens = CheckParameters(
    name="ms_intune_apple_ade_tokens",
    title=Title("Intune Apple ADE Tokens"),
    parameter_form=_parameter_form_ms_intune_apple_ade_tokens,
    topic=Topic.CLOUD,
    condition=HostAndItemCondition(item_title=Title("ADE Token")),
)
