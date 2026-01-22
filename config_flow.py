from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.helpers import config_entry_oauth2_flow, http
from homeassistant.loader import async_get_application_credentials

from .const import BRANDS, CONF_BRAND, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MyHyundaiConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    DOMAIN = DOMAIN
    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self._brand: str | None = None

    @property
    def logger(self) -> logging.Logger:
        return _LOGGER

    async def async_step_user(self, user_input=None):
        if user_input is None:
            schema = vol.Schema({vol.Required(CONF_BRAND): vol.In(BRANDS)})
            return self.async_show_form(step_id="user", data_schema=schema)
        self._brand = user_input[CONF_BRAND]
        return await self.async_step_pick_implementation()

    async def async_step_pick_implementation(self, user_input=None):
        implementations = await config_entry_oauth2_flow.async_get_implementations(
            self.hass, self.DOMAIN
        )
        if self._brand:
            implementations = {
                key: impl
                for key, impl in implementations.items()
                if getattr(impl, "brand", None) == self._brand
            }

        if user_input is not None:
            self.flow_impl = implementations[user_input["implementation"]]
            return await self.async_step_auth()

        if not implementations:
            if self.DOMAIN in await async_get_application_credentials(self.hass):
                return self.async_abort(reason="missing_credentials")
            return self.async_abort(reason="missing_configuration")

        req = http.current_request.get()
        if len(implementations) == 1 and req is not None:
            self.flow_impl = list(implementations.values())[0]
            return await self.async_step_auth()

        return self.async_show_form(
            step_id="pick_implementation",
            data_schema=vol.Schema(
                {
                    vol.Required("implementation"): vol.In(
                        {key: impl.name for key, impl in implementations.items()}
                    )
                }
            ),
        )

    async def async_oauth_create_entry(self, data):
        brand = self._brand or getattr(self.flow_impl, "brand", None)
        if brand:
            if any(
                entry.data.get(CONF_BRAND) == brand
                for entry in self._async_current_entries()
            ):
                return self.async_abort(reason="brand_already_configured")
            data[CONF_BRAND] = brand
            await self.async_set_unique_id(f"{DOMAIN}_{brand}")
            self._abort_if_unique_id_configured()
        title = f"MyHyundai ({BRANDS.get(brand, brand)})" if brand else "MyHyundai"
        return self.async_create_entry(title=title, data=data)
