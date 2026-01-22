"""Application credentials for MyHyundai."""

from __future__ import annotations

import base64
import logging
from typing import Any
from urllib.parse import urlsplit

from aiohttp import ClientError
from yarl import URL

from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import (
    BRAND_GENESIS,
    BRAND_HYUNDAI,
    DOMAIN,
    OAUTH2_GENESIS_AUTHORIZE_URL,
    OAUTH2_GENESIS_TOKEN_URL,
    OAUTH2_HYUNDAI_AUTHORIZE_URL,
    OAUTH2_HYUNDAI_TOKEN_URL,
)

_LOGGER = logging.getLogger(__name__)


class BasicAuthImplementation(AuthImplementation):
    """OAuth2 implementation using HTTP Basic auth for token requests."""

    brand = BRAND_HYUNDAI

    @property
    def redirect_uri(self) -> str:
        try:
            base = get_url(self.hass, prefer_external=True)
        except NoURLAvailableError:
            return config_entry_oauth2_flow.async_get_redirect_uri(self.hass)
        return f"{base}/auth/external/callback"

    async def _token_request(self, data: dict) -> dict:
        session = async_get_clientsession(self.hass)
        auth = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("ascii")
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data.setdefault("client_id", self.client_id)
        _LOGGER.debug("Sending token request to %s", self.token_url)
        resp = await session.post(self.token_url, data=data, headers=headers)
        if resp.status >= 400:
            try:
                error_response = await resp.json()
            except (ClientError, ValueError):
                error_response = {}
            _LOGGER.error("Token request failed: %s", error_response)
        resp.raise_for_status()
        return await resp.json()

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": external_data["code"],
                "redirect_uri": external_data["state"]["redirect_uri"],
            }
        )


class MyHyundaiAuthImplementation(BasicAuthImplementation):
    brand = BRAND_HYUNDAI


class GenesisAuthImplementation(BasicAuthImplementation):
    brand = BRAND_GENESIS

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        redirect_uri = self.redirect_uri
        state = config_entry_oauth2_flow._encode_jwt(  # pylint: disable=protected-access
            self.hass, {"flow_id": flow_id, "redirect_uri": redirect_uri}
        )
        host = urlsplit(redirect_uri).netloc
        return str(
            URL(self.authorize_url).with_query(
                {
                    "clientId": self.client_id,
                    "host": host,
                    "state": state,
                }
            )
        )

    async def _token_request(self, data: dict) -> dict:
        response = await super()._token_request(data)
        success = response.get("success")
        code = response.get("code")
        if success is False or (code and code != "0000"):
            message = response.get("message", "Genesis token request failed")
            raise HomeAssistantError(f"{code}: {message}")
        return response


def _credential_brand(credential: ClientCredential) -> str:
    name = (credential.name or "").lower()
    if "genesis" in name:
        return BRAND_GENESIS
    return BRAND_HYUNDAI


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    brand = _credential_brand(credential)
    if brand == BRAND_GENESIS:
        return GenesisAuthImplementation(
            hass,
            DOMAIN,
            credential,
            authorization_server=AuthorizationServer(
                authorize_url=OAUTH2_GENESIS_AUTHORIZE_URL,
                token_url=OAUTH2_GENESIS_TOKEN_URL,
            ),
        )
    return MyHyundaiAuthImplementation(
        hass,
        DOMAIN,
        credential,
        authorization_server=AuthorizationServer(
            authorize_url=OAUTH2_HYUNDAI_AUTHORIZE_URL,
            token_url=OAUTH2_HYUNDAI_TOKEN_URL,
        ),
    )


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    return {"redirect_url": "https://<your-ha-domain>/auth/external/callback"}
