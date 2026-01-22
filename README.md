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

1. Configure the OAuth Redirect URL in the developer console:
   `https://<your-ha-domain>/auth/external/callback`
2. Configure the Data API Redirect URL for consent callbacks (same base is OK).
3. In Home Assistant, add **Application Credentials**:
   **Settings → Devices & Services → Application Credentials → Add**
   - Create one for Hyundai (name it "Hyundai")
   - Create one for Genesis (name it "Genesis")
4. Add the **MyHyundai** integration:
   **Settings → Devices & Services → Add Integration**
   - Select the brand, then choose the matching credentials

Home Assistant will guide you through the OAuth login.

## Notes for Korea (MyHyundai/Genesis)

This integration is designed for the official Korea APIs. The vehicle
data endpoints must be enabled in your developer application.

## Data consent

The Data API requires a separate 개인정보 제공 동의 flow. If you see
errors like `5005 No Agreement Error` or `4120 Pre-operation is required`,
complete the consent flow in the developer console or via the consent API
before using the integration.

## Environments

The official docs list:
- OAuth2 authorize/token: `prd.kr-ccapi.hyundai.com`
- Hyundai Data APIs: `dev.kr-ccapi.hyundai.com`
- Genesis Data APIs: configure `DATA_API_BASE_GENESIS` once provided

If your account requires production data endpoints, update `DATA_API_BASE`
in `const.py`.

## Entities

### Sensors

- Odometer
- Total driving range
- EV battery (if supported)
- Last updated

### Binary sensors

- Low fuel warning
- Tire pressure warning
- Lamp wire warning
- Smart key battery warning
- Washer fluid warning
- Brake oil warning
- Engine oil warning
- EV battery charging

### Lock

- Door lock (lock/unlock) — requires remote control APIs

### Buttons

- Remote start/stop — requires remote control APIs
