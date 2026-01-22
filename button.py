from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MyHyundaiEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class MyHyundaiButtonDescription(ButtonEntityDescription):
    action: str


BUTTON_DESCRIPTIONS: tuple[MyHyundaiButtonDescription, ...] = (
    MyHyundaiButtonDescription(
        key="remote_start",
        translation_key="remote_start",
        icon="mdi:car-key",
        action="start",
    ),
    MyHyundaiButtonDescription(
        key="remote_stop",
        translation_key="remote_stop",
        icon="mdi:car-off",
        action="stop",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if not coordinator.supports_remote_actions:
        _LOGGER.warning("Remote control API not configured; skipping button entities.")
        return
    vehicles = (coordinator.data or {}).values()
    async_add_entities(
        [
            MyHyundaiButtonEntity(coordinator, vehicle.id, description)
            for vehicle in vehicles
            for description in BUTTON_DESCRIPTIONS
        ]
    )


class MyHyundaiButtonEntity(MyHyundaiEntity, ButtonEntity):
    entity_description: MyHyundaiButtonDescription

    def __init__(
        self,
        coordinator,
        vehicle_id: str,
        description: MyHyundaiButtonDescription,
    ) -> None:
        super().__init__(coordinator, vehicle_id)
        self.entity_description = description
        self._attr_unique_id = f"{vehicle_id}_{description.key}"

    async def async_press(self) -> None:
        if self.entity_description.action == "start":
            await self.coordinator.async_start_climate(self.vehicle_id)
        else:
            await self.coordinator.async_stop_climate(self.vehicle_id)
