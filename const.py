from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "myhyundai"

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.LOCK,
    Platform.BUTTON,
]

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)

OAUTH2_AUTHORIZE_URL = "https://prd.kr-ccapi.hyundai.com/api/v1/user/oauth2/authorize"
OAUTH2_TOKEN_URL = "https://prd.kr-ccapi.hyundai.com/api/v1/user/oauth2/token"

MANUFACTURER = "Hyundai"
