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
# Checkmk ruleset to configure the Microsoft Intune special agent.


from cmk.rulesets.v1 import Help, Message, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    InputHint,
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
        title=Title("Microsoft Intune"),
        help_text=Help(
            "This special agent requests data from Microsoft Intune using the Microsoft Graph API. "
            "To monitor these resources, add this rule to a single host. You must configure "
            "a Microsoft Entra app registration. For the required permissions, see the "
            "help sections under <b>Microsoft Intune services to monitor</b>. "
            "You may also want to adjust the query interval with the rule "
            "<b>Normal check interval for service checks</b>."
        ),
        elements={
            "tenant_id": DictElement(
                parameter_form=String(
                    title=Title("Tenant ID / Directory ID"),
                    help_text=Help("The unique ID from the Microsoft Entra tenant."),
                    field_size=FieldSize.LARGE,
                    custom_validate=[
                        MatchRegex(
                            regex="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                            "[0-9a-fA-F]{12}$",
                            error_msg=Message(
                                "Tenant ID / Directory ID must be in 36-character GUID format."
                            ),
                        ),
                        LengthInRange(
                            min_value=36,
                            error_msg=Message(
                                "Tenant ID / Directory ID must be in 36-character GUID format."
                            ),
                        ),
                    ],
                ),
                required=True,
            ),
            "app_id": DictElement(
                parameter_form=String(
                    title=Title("Client ID / Application ID"),
                    help_text=Help(
                        "The App ID of the Micrsoft Entra app registration for Microsoft Graph API "
                        "requests."
                    ),
                    field_size=FieldSize.LARGE,
                    custom_validate=[
                        MatchRegex(
                            regex="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                            "[0-9a-fA-F]{12}$",
                            error_msg=Message(
                                "Client ID / Application ID must be in 36-character GUID format."
                            ),
                        ),
                        LengthInRange(
                            min_value=36,
                            error_msg=Message(
                                "Client ID / Application ID must be in 36-character GUID format."
                            ),
                        ),
                    ],
                ),
                required=True,
            ),
            "app_secret": DictElement(
                parameter_form=Password(
                    title=Title("Client secret"),
                    help_text=Help("The client secret from the Microsoft Entra app registration."),
                ),
                required=True,
            ),
            "proxy": DictElement(
                parameter_form=Proxy(
                    title=Title("HTTP proxy"),
                    help_text=Help(
                        "The HTTP proxy used to connect to the Microsoft Graph API. If not set, "
                        "the environment settings will be used."
                    ),
                ),
            ),
            "services_to_monitor": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Microsoft Intune services to monitor"),
                    help_text=Help(
                        "Select the Microsoft Intune services that you want to monitor. Ensure "
                        "that you add the required Microsoft Graph API permissions to your "
                        "Microsoft Entra app registration and grant admin consent to them. For"
                        "App licenses, you must configure at least the "
                        "<tt>DeviceManagementApps.Read.All</tt> API application permission. "
                        "For Apple ADE tokens, Apple MDM push certificate and VPP tokens, you"
                        "must configure at least the "
                        "<tt>DeviceManagementServiceConfig.Read.All</tt> API application "
                        "permission. For Certificate connectors, you must configure at least the "
                        "<tt>DeviceManagementConfiguration.Read.All</tt> API application "
                        "permission. "
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
                                "Select one or more <b>Microsoft Intune services to monitor</b>"
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
            "timeout": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Timeout for each API request"),
                    help_text=Help(
                        "Define a custom timeout in seconds to use for each API request. The "
                        "timeout is used for token request and any service that should be "
                        "monitored. The default timeout is 10s."
                    ),
                    displayed_magnitudes=[TimeMagnitude.SECOND],
                    prefill=InputHint(10.0),
                    custom_validate=[
                        NumberInRange(
                            min_value=3,
                            max_value=600,
                            error_msg=Message("The timeout must be between 3s and 600s."),
                        ),
                    ],
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
