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
# CHECKMK RULESET: Microsoft Intune (special agent)
#
# This file provides the parameter definitions for integrating Microsoft Intune monitoring into
# Checkmk.
# Microsoft Intune is a Checkmk special agent (ms_intune).
####################################################################################################

from cmk.rulesets.v1 import Help, Message, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    MultipleChoice,
    MultipleChoiceElement,
    Password,
    Proxy,
    String,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.form_specs.validators import LengthInRange, MatchRegex, NumberInRange
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _parameter_form_special_agent_ms_intune() -> Dictionary:
    return Dictionary(
        title=Title("Special agent parameters"),
        help_text=Help(
            "This special agent retrieves data about <b>Microsoft Intune</b> using the <b> "
            "Microsoft Graph API</b>.<br>To monitor these resources, apply this rule to a "
            "<b>single host</b>.<br>You must configure a <b>Microsoft Entra app registration</b>. "
            "For details on the required permissions, see the help section under <b>Microsoft "
            "Intune services to monitor</b>.<br><b>Tip:</b> You can adjust the query interval "
            "using the rule <b>Normal check interval for service checks</b> to limit the number of "
            "API requests.<br><b>Pro tip:</b> To optimize API usage and reduce system load, you "
            "rule to a can create this rule multiple times with different service selections and "
            "assign each separate host with a specific check interval.<br>This allows you to "
            "tailor the monitoring frequency per service. For example, create one rule for just "
            "<b>Certificate Connectors</b> on a host with a 5-minute interval and another rule for "
            "the tokens and certificates on a host with a 30-minute interval."
        ),
        elements={
            "tenant_id": DictElement(
                parameter_form=String(
                    title=Title("Tenant ID / directory ID"),
                    help_text=Help(
                        "The unique ID from the Microsoft Entra tenant.<br>For example, you can "
                        "find this ID on the <b>Overview</b> page of the Microsoft Entra app "
                        "registration."
                    ),
                    field_size=FieldSize.LARGE,
                    custom_validate=[
                        MatchRegex(
                            regex="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                            "[0-9a-fA-F]{12}$",
                            error_msg=Message(
                                "The <b>Tenant ID / directory ID</b> must be in 36-character GUID "
                                "format (e.g., <tt>123e4567-e89b-12d3-a456-426614174000</tt>)."
                            ),
                        ),
                        LengthInRange(
                            min_value=36,
                            error_msg=Message(
                                "The <b>Tenant ID / directory ID</b> must be in 36-character GUID "
                                "format (e.g., <tt>123e4567-e89b-12d3-a456-426614174000</tt>)."
                            ),
                        ),
                    ],
                ),
                required=True,
            ),
            "app_id": DictElement(
                parameter_form=String(
                    title=Title("Client ID / application ID"),
                    help_text=Help(
                        "The application ID of the Microsoft Entra app registration. This "
                        "application is required for the requests to the Microsoft Graph API.<br>"
                        "For example, you can find this ID on the <b>Overview</b> page of the "
                        "Microsoft Entra app registration."
                    ),
                    field_size=FieldSize.LARGE,
                    custom_validate=[
                        MatchRegex(
                            regex="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                            "[0-9a-fA-F]{12}$",
                            error_msg=Message(
                                "The <b>Client ID / application ID</b> must be in 36-character "
                                "GUID format (e.g., <tt>123e4567-e89b-12d3-a456-426614174000</tt>)."
                            ),
                        ),
                        LengthInRange(
                            min_value=36,
                            error_msg=Message(
                                "The <b>Client ID / application ID</b> must be in 36-character "
                                "GUID format (e.g., <tt>123e4567-e89b-12d3-a456-426614174000</tt>)."
                            ),
                        ),
                    ],
                ),
                required=True,
            ),
            "app_secret": DictElement(
                parameter_form=Password(
                    title=Title("Client secret"),
                    help_text=Help(
                        "The client secret value of the Microsoft Entra app registration."
                    ),
                ),
                required=True,
            ),
            "services_to_monitor": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Microsoft Intune services to monitor"),
                    help_text=Help(
                        "Select the Microsoft Intune services that you want to monitor.<br>"
                        "Ensure that you add the required Microsoft Graph API permissions "
                        "to your Microsoft Entra app registration and grant admin consent to them."
                        "<br><br>Minimum API <b>application</b> permissions:<ul>"
                        "<li><b>App licenses</b>: <tt>DeviceManagementApps.Read.All</tt></li>"
                        "<li><b>Apple ADE tokens</b>: <tt>DeviceManagementServiceConfig.Read.All"
                        "</tt></li><li><b>Apple MDM push certificate</b>: <tt>"
                        "DeviceManagementServiceConfig.Read.All</tt></li><li><b>VPP tokens</b>: "
                        "<tt>DeviceManagementServiceConfig.Read.All</tt></li><li><b>Certificate "
                        "connectors</b>: <tt>DeviceManagementConfiguration.Read.All</tt></li></ul>"
                    ),
                    elements=[
                        MultipleChoiceElement(
                            name="app_licenses",
                            title=Title("App licenses"),
                        ),
                        MultipleChoiceElement(
                            name="apple_ade_tokens",
                            title=Title("Apple ADE tokens (Automated Device Enrollment)"),
                        ),
                        MultipleChoiceElement(
                            name="apple_mdm_push_cert",
                            title=Title("Apple MDM push certificate"),
                        ),
                        MultipleChoiceElement(
                            name="vpp_tokens",
                            title=Title("Apple VPP tokens (Volume Purchase Program)"),
                        ),
                        MultipleChoiceElement(
                            name="cert_connectors",
                            title=Title("Certificate connectors"),
                        ),
                    ],
                    custom_validate=[
                        LengthInRange(
                            min_value=1,
                            error_msg=Message(
                                "Select at least one of the <b>Microsoft Intune services to monitor"
                                "</b>."
                            ),
                        ),
                    ],
                    prefill=DefaultValue(
                        [
                            "app_licenses",
                            "apple_ade_tokens",
                            "apple_mdm_push_cert",
                            "cert_connectors",
                            "vpp_tokens",
                        ]
                    ),
                ),
                required=True,
            ),
            "proxy": DictElement(
                parameter_form=Proxy(
                    title=Title("HTTP proxy"),
                    help_text=Help(
                        "Configure HTTP proxy settings for the API connections.<br><br>"
                        "If not configured, the system environment proxy settings will be used."
                    ),
                ),
            ),
            "timeout": DictElement(
                parameter_form=TimeSpan(
                    title=Title("API request timeout"),
                    help_text=Help(
                        "Specify a custom timeout (in seconds) for each API request.<br>"
                        "This timeout applies to the token request as well as any monitored service"
                        ".<br><br>If not specified, the default timeout is <b>10 seconds</b>."
                    ),
                    displayed_magnitudes=[TimeMagnitude.SECOND],
                    custom_validate=[
                        NumberInRange(
                            min_value=3,
                            max_value=600,
                            error_msg=Message(
                                "The <b>API request timeout</b> must be between 3s and 600s."
                            ),
                        ),
                    ],
                    prefill=DefaultValue(10.0),
                ),
            ),
        },
    )


rule_spec_ms_intune = SpecialAgent(
    name="ms_intune",
    title=Title("Microsoft Intune"),
    parameter_form=_parameter_form_special_agent_ms_intune,
    topic=Topic.CLOUD,
)
