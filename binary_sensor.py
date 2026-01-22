from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import MyHyundaiEntity


@dataclass(frozen=True, kw_only=True)
class MyHyundaiBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[Any], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[MyHyundaiBinarySensorDescription, ...] = (
    MyHyundaiBinarySensorDescription(
        key="low_fuel_warning",
        translation_key="low_fuel_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.low_fuel_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="tire_pressure_warning",
        translation_key="tire_pressure_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.tire_pressure_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="lamp_wire_warning",
        translation_key="lamp_wire_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.lamp_wire_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="smart_key_battery_warning",
        translation_key="smart_key_battery_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.smart_key_battery_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="washer_fluid_warning",
        translation_key="washer_fluid_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.washer_fluid_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="brake_oil_warning",
        translation_key="brake_oil_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.brake_oil_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="engine_oil_warning",
        translation_key="engine_oil_warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda vehicle: vehicle.engine_oil_warning,
    ),
    MyHyundaiBinarySensorDescription(
        key="ev_battery_is_charging",
        translation_key="ev_battery_charging",
        value_fn=lambda vehicle: vehicle.ev_battery_is_charging,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    vehicles = (coordinator.data or {}).values()
    async_add_entities(
        [
            MyHyundaiBinarySensorEntity(coordinator, vehicle.id, description)
            for vehicle in vehicles
            for description in BINARY_SENSOR_DESCRIPTIONS
        ]
    )


class MyHyundaiBinarySensorEntity(MyHyundaiEntity, BinarySensorEntity):
    entity_description: MyHyundaiBinarySensorDescription

    def __init__(
        self,
        coordinator,
        vehicle_id: str,
        description: MyHyundaiBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, vehicle_id)
        self.entity_description = description
        self._attr_unique_id = f"{vehicle_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        vehicle = self.coordinator.get_vehicle(self.vehicle_id)
        if vehicle is None:
            return None
        return self.entity_description.value_fn(vehicle)
