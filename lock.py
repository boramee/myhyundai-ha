from __future__ import annotations

import logging

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MyHyundaiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.supports_remote_actions:
        _LOGGER.warning("Remote control API not configured; skipping lock entities.")
        return
    vehicles = (coordinator.data or {}).values()
    async_add_entities(
        [MyHyundaiDoorLock(coordinator, vehicle.id) for vehicle in vehicles]
    )


class MyHyundaiDoorLock(MyHyundaiEntity, LockEntity):
    _attr_translation_key = "door_lock"

    def __init__(self, coordinator, vehicle_id: str) -> None:
        super().__init__(coordinator, vehicle_id)
        self._attr_unique_id = f"{vehicle_id}_door_lock"

    @property
    def is_locked(self) -> bool | None:
        vehicle = self.coordinator.get_vehicle(self.vehicle_id)
        if vehicle is None:
            return None
        return vehicle.is_locked

    async def async_lock(self, **kwargs) -> None:
        await self.coordinator.async_lock(self.vehicle_id)

    async def async_unlock(self, **kwargs) -> None:
        await self.coordinator.async_unlock(self.vehicle_id)
