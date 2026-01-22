"""Application credentials for MyHyundai."""

from __future__ import annotations

import base64
import logging
from typing import Any

from aiohttp import ClientError

from homeassistant.components.application_credentials import (
    AuthImplementation,
    AuthorizationServer,
    ClientCredential,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, OAUTH2_AUTHORIZE_URL, OAUTH2_TOKEN_URL

_LOGGER = logging.getLogger(__name__)


class MyHyundaiAuthImplementation(AuthImplementation):
    """OAuth2 implementation using HTTP Basic auth for token requests."""

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


async def async_get_auth_implementation(
    hass: HomeAssistant, auth_domain: str, credential: ClientCredential
) -> config_entry_oauth2_flow.AbstractOAuth2Implementation:
    return MyHyundaiAuthImplementation(
        hass,
        DOMAIN,
        credential,
        authorization_server=AuthorizationServer(
            authorize_url=OAUTH2_AUTHORIZE_URL,
            token_url=OAUTH2_TOKEN_URL,
        ),
    )


async def async_get_description_placeholders(hass: HomeAssistant) -> dict[str, str]:
    return {"redirect_url": "https://<your-ha-domain>/auth/external/callback"}
