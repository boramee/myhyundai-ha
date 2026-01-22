# MyHyundai (unofficial) Home Assistant integration

This is a minimal custom integration that uses the official
MyHyundai OAuth2 APIs to authenticate and read vehicle data.

## Requirements

- MyHyundai (Korea) account
- Approved MyHyundai developer application (Client ID/Secret)
- Home Assistant with custom component support
- External URL configured for OAuth callback

## Install (git clone into custom_components)

```bash
cd /config/custom_components
git clone git@github.com:boramee/myhyundai-ha.git myhyundai
```

Then restart Home Assistant.

## Install (manual copy)

1. Copy this repository into a temporary folder.
2. Copy the files into `custom_components/myhyundai`.
3. Restart Home Assistant.

## Setup

1. Configure the OAuth Redirect URL in the MyHyundai developer console:
   `https://<your-ha-domain>/auth/external/callback`
2. In Home Assistant, add **Application Credentials** for MyHyundai:
   **Settings → Devices & Services → Application Credentials → Add**
3. Add the **MyHyundai** integration:
   **Settings → Devices & Services → Add Integration**

Home Assistant will guide you through the OAuth login.

## Notes for Korea (MyHyundai)

This integration is designed for the official Korea APIs. The vehicle
data endpoints must be enabled in your developer application.

## Entities

### Sensors

- Odometer
- Total driving range
- Fuel level
- Car battery
- EV battery (if supported)
- Air temperature
- Last updated

### Binary sensors

- Engine running
- Hood open
- Trunk open

### Lock

- Door lock (lock/unlock) — requires remote control APIs

### Buttons

- Remote start/stop — requires remote control APIs
