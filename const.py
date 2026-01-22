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

CONF_BRAND = "brand"
BRAND_HYUNDAI = "hyundai"
BRAND_GENESIS = "genesis"
BRANDS = {
    BRAND_HYUNDAI: "Hyundai",
    BRAND_GENESIS: "Genesis",
}

OAUTH2_HYUNDAI_AUTHORIZE_URL = (
    "https://prd.kr-ccapi.hyundai.com/api/v1/user/oauth2/authorize"
)
OAUTH2_HYUNDAI_TOKEN_URL = "https://prd.kr-ccapi.hyundai.com/api/v1/user/oauth2/token"
OAUTH2_GENESIS_AUTHORIZE_URL = "https://accounts.genesis.com/api/authorize/ccsp/oauth"
OAUTH2_GENESIS_TOKEN_URL = (
    "https://accounts.genesis.com/api/account/ccsp/user/oauth2/token"
)

USER_API_BASE_HYUNDAI = "https://prd.kr-ccapi.hyundai.com/api/v1"
USER_API_BASE_GENESIS = "https://prd-kr-ccapi.genesis.com:8081/api/v1"
DATA_API_BASE_HYUNDAI = "https://dev.kr-ccapi.hyundai.com/api/v1"
DATA_API_BASE_GENESIS = ""

MANUFACTURER = "Hyundai"
