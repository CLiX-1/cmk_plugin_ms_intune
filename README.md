# Checkmk Plugin: Microsoft Intune Special Agent

## Plugin Information
The Microsoft Intune Special Agent can be integrated into Checkmk 2.3 or newer.

You can download the .mkp file from releases in this repository to upload it directly to your Checkmk site.

The Plugin provides monitoring of these components:
- Intune App Licenses
- Intune Apple ADE Tokens (Automated Device Enrollment)
- Intune Apple MDM Push Certificate
- Intune Apple VPP Tokens (Volume Purchase Program)
- Intune Certificate Connectors

## Prerequisites

This Special Agent uses the Microsoft Graph API to collect the monitoring data.
To access the API, you need a Microsoft Entra Tenant and a Microsoft Entra App Registration with a secret.

You need at least these API **application** permissions for your App Registration:
- *DeviceManagementApps.Read.All*
- *DeviceManagementConfiguration.Read.All*
- *DeviceManagementServiceConfig.Read.All*

For a more granular option, the required API permissions per check are listed in the next sections.

To implement the check, you need to configure the *Microsoft Intune* Special Agent in Checkmk.
You will need the Microsoft Entra Tenant ID, the Microsoft Entra App Registration ID and Secret.
When you configure the Special Agent, you have the option to select only the services that you want to monitor. You do not have to implement all the checks, but at least one of them.

## Intune App Licenses

### Description

This check monitors available application licenses from Microsoft Intune. 
Only applications with a publishingState of "published" are queried.
If the application does not have a "totalLicenseCount" attribute, it is ignored.

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/f46cc3b2-5a4e-4377-9e51-3275019a1533)

### Checkmk Parameters

1. **Licenses lower levels**: Set lower-level thresholds for the number of remaining available app licenses as absolute or percentage values. To ignore the remaining available licenses, Select "Percentage" or "Absolute" and "No levels".
2. **Activate thresholds at total licenses**: Set the total number of licenses at which the thresholds will be calclulated. If the number of licenses is less, then the thresholds will be ignored.

### Microsoft Graph API

**API permissions**: At  least *DeviceManagementApps.Read.All* (Application permission)

**Endpoint**: *https://graph.microsoft.com/beta/deviceAppManagement/mobileApps*

2024-07-17: The beta endpoint is required, because only the iosVppApp is available in the 1.0 API version.

### Known issues

- Some applications are universal applications. For example, they are valid for both iOS and macOS and counted together. These will appear as two services with the same counts.

## Intune Apple ADE Tokens

### Description

This check monitors the Apple Automated Device Enrollment (ADE) token expiration time configured in Microsoft Intune.
You need this token to enroll Apple devices directly into Microsoft Intune from Apple Business Manager or Apple School Manager and apply settings without an administrator touching the device.
Apple Automated Device Enrollment (ADE) was formerly known as the Apple Device Enrollment Program (DEP).

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/20e2df05-1725-4181-9149-f98e237968f1)

### Checkmk Parameters

1. **Licenses lower levels**: Specify the lower levels for the Apple ADE token expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore token expiration, select 'No levels'.

### Microsoft Graph API endpoints

**API permissions**: At  least *DeviceManagementServiceConfig.Read.All* (Application permission)

*https://graph.microsoft.com/beta/deviceAppManagement/mobileApps*

2024-07-17: The endpoint is only available in the beta API version.

## Intune Apple MDM Push Certificate

### Description

This check monitors the Apple MDM push certificate expiration time configured in Microsoft Intune.
You need this certificate to manage and enroll Apple devices in Microsoft Intune.

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/a5bf6bff-33b0-4831-a6e0-463eb61f42ce)

### Checkmk Parameters

1. **Licenses lower levels**: Specify the lower levels for the Apple MDM push certificate expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore the certificate expiration, select 'No levels'.

### Microsoft Graph API endpoints

**API permissions**: At  least *DeviceManagementServiceConfig.Read.All* (Application permission)

*https://graph.microsoft.com/v1.0/deviceManagement/applePushNotificationCertificate*

## Intune Apple VPP Tokens

### Description

This check monitors the Apple Volume Purchase Program (VPP) token expiration time and state configured in Microsoft Intune.
You need this token to manage and distribute applications purchased through Apple Volume Purchase Program with Microsoft Intune.

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/b2c046c8-fe91-4aee-a750-7189121cfe4c)

### Checkmk Parameters

1. **Licenses lower levels**: Specify the lower levels for the Apple VPP token expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore token expiration, select 'No levels'.
   
### Microsoft Graph API endpoints

**API permissions**: At  least *DeviceManagementServiceConfig.Read.All* (Application permission)

*https://graph.microsoft.com/beta/deviceAppManagement/vppTokens*

2024-07-17: The beta endpoint is required, because the "displayName" attribute is not available in the 1.0 API version

## Intune Certificate Connectors

### Description

This check monitors the health of the certificate connectors connected with Microsoft Intune.
Certificate connectors allow you to deploy certificates to devices that are enrolled in Microsoft Intune.

### Checkmk service example

![grafik](https://github.com/user-attachments/assets/2dab1f8e-5faf-460c-850f-635037ce56d7)

### Checkmk Parameters

No parameters available for configuration.

### Microsoft Graph API endpoints

**API permissions**: At  least *DeviceManagementConfiguration.Read.All* (Application permission)

*https://graph.microsoft.com/beta/deviceManagement/ndesConnectors*

2024-07-17: The endpoint is only available in the beta API version.
