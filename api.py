from __future__ import annotations

import logging

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_entry_oauth2_flow

from .models import MyHyundaiVehicle

_LOGGER = logging.getLogger(__name__)


class MyHyundaiApi:
    def __init__(self) -> None:
        self.supports_remote_actions = False

    async def async_get_vehicles(
        self, session: config_entry_oauth2_flow.OAuth2Session
    ) -> dict[str, MyHyundaiVehicle]:
        _LOGGER.warning("Vehicle list API not configured yet.")
        return {}

    async def async_lock(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle_id: str
    ) -> None:
        raise HomeAssistantError("Remote control API not configured yet.")

    async def async_unlock(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle_id: str
    ) -> None:
        raise HomeAssistantError("Remote control API not configured yet.")

    async def async_remote_start(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle_id: str
    ) -> None:
        raise HomeAssistantError("Remote start API not configured yet.")

    async def async_remote_stop(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle_id: str
    ) -> None:
        raise HomeAssistantError("Remote stop API not configured yet.")
