#!/usr/bin/env python3
# -*- coding: utf-8; py-indent-offset: 4; max-line-length: 100 -*-

# Copyright (C) 2025  Christopher Pommer <cp.software@outlook.de>

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
# Checkmk ruleset to set the expiration time thresholds for the Apple MDM push certificate.
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
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _parameter_form_ms_intune_apple_push_cert() -> Dictionary:
    return Dictionary(
        title=Title("Intune Apple MDM Push Certificate"),
        help_text=Help(
            "Parameters for the expiration time thresholds from the Apple MDM push certificate "
            "configured in Microsoft Intune. "
            "To use this service, you need to set up the <b>Microsoft Intune</b> special agent."
        ),
        elements={
            "cert_expiration": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Certificate expiration"),
                    help_text=Help(
                        "Specify the lower levels for the Apple MDM push certificate expiration "
                        "time. The default values are 14 days (WARN) and 5 days (CRIT). "
                        "To ignore the certificate expiration, select 'No levels'."
                    ),
                    form_spec_template=TimeSpan(
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


rule_spec_ms_intune_apple_mdm_push_cert = CheckParameters(
    name="ms_intune_apple_mdm_push_cert",
    title=Title("Intune Apple MDM Push Certificate"),
    parameter_form=_parameter_form_ms_intune_apple_push_cert,
    topic=Topic.CLOUD,
    condition=HostCondition(),
)
