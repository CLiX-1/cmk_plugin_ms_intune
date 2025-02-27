# Checkmk Plugin: Microsoft Intune Special Agent

## Plugin Information
The Microsoft Intune Special Agent can be integrated into Checkmk 2.3 or newer.

You can download the `.mkp` file from the [releases](../../releases) in this repository and upload it directly to your Checkmk site.

The Plugin provides monitoring for the following components:
- Intune App Licenses
- Intune Apple ADE Tokens (Automated Device Enrollment)
- Intune Apple MDM Push Certificate
- Intune Apple VPP Tokens (Volume Purchase Program)
- Intune Certificate Connectors

## Prerequisites

This Special Agent uses the Microsoft Graph API to collect the monitoring data.
To access the API, you need a Microsoft Entra tenant and a Microsoft Entra app registration with a client secret.

You need at least the following API **application** permissions for your app registration to use all the checks:
- *DeviceManagementApps.Read.All*
- *DeviceManagementConfiguration.Read.All*
- *DeviceManagementServiceConfig.Read.All*

For a more granular option, the required API permissions per check are listed in the next sections.


To implement the check, you need to configure the *Microsoft Intune* Special Agent in Checkmk.
You will need the Microsoft Entra tenant ID, the Microsoft Entra app registration ID and the client secret.
When you configure the Special Agent, you have the option to select only the services that you want to monitor. You do not have to implement all the checks, but at least one of them.

This plugin uses HTTPS connections to Microsoft.
Make sure you have enabled **Trust system-wide configured CAs** or uploaded the CA certificates for the Microsoft domains in Checkmk.
You can find these options in **Setup** > **Global settings** > **Trusted certificate authorities for SSL** under **Site management**.
If your system does not trust the certificate you will encounter the error: `certificate verify failed: unable to get local issuer certificate`.

Also do not block the communications to:
- https://login.microsoftonline.com
- https://graph.microsoft.com


## Check Details
### Intune App Licenses

#### Description

This check monitors available application licenses from Microsoft Intune.
Only applications with a publishingState of `published` are queried.
If an application does not have a `totalLicenseCount` attribute, it is ignored.

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/f46cc3b2-5a4e-4377-9e51-3275019a1533)

#### Checkmk Parameters

1. **Licenses Lower Levels**: Set lower thresholds for the number of remaining available app licenses as absolute or percentage values. To ignore the remaining available licenses, select "Percentage" or "Absolute" and "No levels".
2. **Activate Thresholds at Total Licenses**: Define the total number of licenses at which the thresholds will be calculated. If the number of licenses is lower than this value, then the thresholds will be ignored.

#### Microsoft Graph API

**API Permissions**: At least *DeviceManagementApps.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/beta/deviceAppManagement/mobileApps`

2025-01-27: The beta endpoint is required, because only the `iosVppApp` is available in the 1.0 API version.

#### Known Issues

- Some applications are universal applications. For example, they are valid for both iOS and macOS and are counted together. These will appear as two services with the same counts.

### Intune Apple ADE Tokens

#### Description

This check monitors the Apple Automated Device Enrollment (ADE) token expiration time configured in Microsoft Intune.
You need this token to enroll Apple devices directly into Microsoft Intune from Apple Business Manager or Apple School Manager and apply settings without an administrator touching the device.
Apple Automated Device Enrollment (ADE) was formerly known as the Apple Device Enrollment Program (DEP).

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/20e2df05-1725-4181-9149-f98e237968f1)

#### Checkmk Parameters

1. **Licenses Lower Levels**: Specify the lower thresholds for the Apple ADE token expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore token expiration, select "No levels".

#### Microsoft Graph API Endpoints

**API Permissions**: At least *DeviceManagementServiceConfig.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/beta/deviceAppManagement/mobileApps`

2025-02-27: This endpoint is only available in the beta API version.

### Intune Apple MDM Push Certificate

#### Description

This check monitors the Apple MDM push certificate expiration time configured in Microsoft Intune.
You need this certificate to manage and enroll Apple devices in Microsoft Intune.

#### Checkmk ServiceEexample

![grafik](https://github.com/user-attachments/assets/a5bf6bff-33b0-4831-a6e0-463eb61f42ce)

#### Checkmk Parameters

1. **Licenses Lower Levels**: Specify the lower thresholds for the Apple MDM push certificate expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore the certificate expiration, select "No levels".

#### Microsoft Graph API endpoints

**API Permissions**: At least *DeviceManagementServiceConfig.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/v1.0/deviceManagement/applePushNotificationCertificate`

### Intune Apple VPP Tokens

#### Description

This check monitors the Apple Volume Purchase Program (VPP) token expiration time and state configured in Microsoft Intune.
You need this token to manage and distribute applications purchased through the Apple Volume Purchase Program with Microsoft Intune.

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/b2c046c8-fe91-4aee-a750-7189121cfe4c)

#### Checkmk Parameters

1. **Licenses Lower Levels**: Specify the lower thresholds for the Apple VPP token expiration time. The default values are 14 days (WARN) and 5 days (CRIT). To ignore token expiration, select "No levels".

#### Microsoft Graph API endpoints

**API permissions**: At least *DeviceManagementServiceConfig.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/beta/deviceAppManagement/vppTokens`

2025-02-27: The beta endpoint is required, because the `displayName` attribute is not available in the 1.0 API version

### Intune Certificate Connectors

#### Description

This check monitors the health of the certificate connectors connected to Microsoft Intune.
Certificate connectors allow you to deploy certificates to devices that are enrolled in Microsoft Intune.

#### Checkmk Service Example

![grafik](https://github.com/user-attachments/assets/2dab1f8e-5faf-460c-850f-635037ce56d7)

#### Checkmk Parameters

No parameters are available for configuration.

#### Microsoft Graph API Endpoints

**API Permissions**: At least *DeviceManagementConfiguration.Read.All* (Application permission)

**Endpoint**: `https://graph.microsoft.com/beta/deviceManagement/ndesConnectors`

2025-02-27: This endpoint is only available in the beta API version.

## Steps to Get It Working

To use this Checkmk Special Agent, you must configure a Microsoft Entra application to access the Microsoft Graph API endpoints.
You must also have a host in Checkmk and configure the Special Agent rule for the host.

### Microsoft Entra Configuration
#### Register an Application

1. Sign in to the Microsoft Entra Admin Center (https://entra.microsoft.com) as a Global Administrator (or at least a Privileged Role Administrator)
2. Browse to **Identity** > **Applications** > **App registrations**
3. Select **New registration**
4. Provide a meaningful name (e.g. "Checkmk Special Agent")
5. Select **Accounts in this organizational directory only**
6. Do not specify a **Redirect URI**
7. Click **Register**

> [!NOTE]
> In the overview of your new application registration, you will find the **Application (client) ID** and the **Directory (tenant) ID**.
> You will need this information later for the configuration of the Checkmk Special Agent.

#### Configure the Application
1. Go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Add all API permissions for all services that you want to monitor (see sections above)
4. Select **Grant admin consent** > **Yes**
5. Go to **Certificates & secrets** and click **New client secret**
6. Enter a description (e.g. the Checkmk Site name) and select an expiration period for the secret

### Checkmk Special Agent Configuration

1. Log in to your Checkmk site

#### Add a New Password

1. Browse to **Setup** > **Passwords**
2. Select **Add password**
3. Specify a **Unique ID** and a **Title**
4. Copy the generated secret from the Microsoft Entra Admin Center to the **Password** field
5. Click **Save**

#### Add Checkmk Host

1. Add a new host in **Setup** > **Hosts**
2. Configure your custom settings and set
    -   **IP address family**: No IP
    -   **Checkmk agent / API integrations**: API integrations if configured, else Checkmk agent
3. Save

#### Add Special Agent Rule

1. Navigate to the Special Agent rule **Setup** > **Microsoft Intune** (use the search bar)
2. Add a new rule and configure the required settings
    -   **Application (client) ID** and **Directory (tenant) ID** from the Microsoft Entra Application
    -   For **Client secret** select **From password store** and the password from **Add a New Password**
    -   Select all services that you want to monitor
    -   Add the newly created host in **Explicit hosts**
3. Save and go to your new host and discover your new services
4. Activate the changes

