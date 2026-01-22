from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyHyundaiApi
from .const import BRAND_HYUNDAI, CONF_BRAND, DEFAULT_UPDATE_INTERVAL
from .models import MyHyundaiVehicle

_LOGGER = logging.getLogger(__name__)


class MyHyundaiCoordinator(DataUpdateCoordinator[dict[str, MyHyundaiVehicle]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="myhyundai",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.entry = entry
        self._session: config_entry_oauth2_flow.OAuth2Session | None = None
        brand = entry.data.get(CONF_BRAND, BRAND_HYUNDAI)
        self.api = MyHyundaiApi(brand)

    async def _async_get_session(self) -> config_entry_oauth2_flow.OAuth2Session:
        if self._session is None:
            implementation = (
                await config_entry_oauth2_flow.async_get_config_entry_implementation(
                    self.hass, self.entry
                )
            )
            self._session = config_entry_oauth2_flow.OAuth2Session(
                self.hass, self.entry, implementation
            )
        return self._session

    async def _async_update_data(self) -> dict[str, MyHyundaiVehicle]:
        try:
            session = await self._async_get_session()
            return await self.api.async_get_vehicles(session)
        except HomeAssistantError as err:
            raise UpdateFailed(str(err)) from err

    def get_vehicle(self, vehicle_id: str) -> MyHyundaiVehicle | None:
        if not self.data:
            return None
        return self.data.get(vehicle_id)

    @property
    def supports_remote_actions(self) -> bool:
        return self.api.supports_remote_actions

    async def async_lock(self, vehicle_id: str) -> None:
        session = await self._async_get_session()
        await self.api.async_lock(session, vehicle_id)
        await self.async_request_refresh()

    async def async_unlock(self, vehicle_id: str) -> None:
        session = await self._async_get_session()
        await self.api.async_unlock(session, vehicle_id)
        await self.async_request_refresh()

    async def async_start_climate(self, vehicle_id: str) -> None:
        session = await self._async_get_session()
        await self.api.async_remote_start(session, vehicle_id)
        await self.async_request_refresh()

    async def async_stop_climate(self, vehicle_id: str) -> None:
        session = await self._async_get_session()
        await self.api.async_remote_stop(session, vehicle_id)
        await self.async_request_refresh()
