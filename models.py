from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MyHyundaiVehicle:
    id: str
    name: str | None = None
    model: str | None = None
    vin: str | None = None
    car_type: str | None = None
    odometer: float | None = None
    odometer_unit: str | None = None
    total_driving_range: float | None = None
    total_driving_range_unit: str | None = None
    fuel_level: float | None = None
    car_battery_percentage: int | None = None
    ev_battery_percentage: int | None = None
    ev_battery_is_charging: bool | None = None
    ev_battery_plugin: int | None = None
    air_temperature: float | None = None
    last_updated_at: datetime | None = None
    engine_is_running: bool | None = None
    hood_is_open: bool | None = None
    trunk_is_open: bool | None = None
    is_locked: bool | None = None
    low_fuel_warning: bool | None = None
    tire_pressure_warning: bool | None = None
    lamp_wire_warning: bool | None = None
    smart_key_battery_warning: bool | None = None
    washer_fluid_warning: bool | None = None
    brake_oil_warning: bool | None = None
    engine_oil_warning: bool | None = None
