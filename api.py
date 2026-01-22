from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.util import dt as dt_util

from .const import DATA_API_BASE, USER_API_BASE
from .models import MyHyundaiVehicle

_LOGGER = logging.getLogger(__name__)

DISTANCE_UNITS = {
    0: "ft",
    1: "km",
    2: "m",
    3: "mi",
}

CONSENT_REQUIRED_CODES = {
    "5005": "개인정보 제공 동의가 필요합니다.",
    "4014": "서비스 약관이 등록되지 않았습니다.",
    "4120": "사전 동의 절차가 필요합니다.",
}

ALLOW_NO_DATA_CODES = {"4045", "4046"}


class MyHyundaiApi:
    def __init__(self) -> None:
        self.supports_remote_actions = False

    async def async_get_vehicles(
        self, session: config_entry_oauth2_flow.OAuth2Session
    ) -> dict[str, MyHyundaiVehicle]:
        carlist = await self._request_json(
            session,
            "GET",
            f"{DATA_API_BASE}/car/profile/carlist",
            allow_error_codes=ALLOW_NO_DATA_CODES,
        )
        if not carlist or "cars" not in carlist:
            _LOGGER.warning("No vehicles returned from API.")
            return {}

        vehicles: dict[str, MyHyundaiVehicle] = {}
        for car in carlist.get("cars", []):
            vehicle_id = car.get("carId")
            if not vehicle_id:
                continue
            name = car.get("carNickname") or car.get("carSellname") or car.get("carName")
            model = car.get("carSellname") or car.get("carName")
            vehicle = MyHyundaiVehicle(
                id=vehicle_id,
                name=name,
                model=model,
            )

            await self._populate_vehicle_status(session, vehicle, car.get("carType"))
            vehicles[vehicle.id] = vehicle

        return vehicles

    async def _populate_vehicle_status(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle: MyHyundaiVehicle, car_type: str | None
    ) -> None:
        dte = await self._request_json(
            session,
            "GET",
            f"{DATA_API_BASE}/car/status/{vehicle.id}/dte",
            allow_error_codes=ALLOW_NO_DATA_CODES,
        )
        if dte:
            vehicle.total_driving_range = dte.get("value")
            vehicle.total_driving_range_unit = DISTANCE_UNITS.get(dte.get("unit"))
            self._update_last_updated(vehicle, dte.get("timestamp"))

        odometer = await self._request_json(
            session,
            "GET",
            f"{DATA_API_BASE}/car/status/{vehicle.id}/odometer",
            allow_error_codes=ALLOW_NO_DATA_CODES,
        )
        if odometer:
            entries = odometer.get("odometers", [])
            if entries:
                latest = max(entries, key=lambda entry: entry.get("timestamp", ""))
                vehicle.odometer = latest.get("value")
                vehicle.odometer_unit = DISTANCE_UNITS.get(latest.get("unit"))
                self._update_last_updated(vehicle, latest.get("timestamp"))

        if car_type in {"EV", "PHEV", "FCEV"}:
            battery = await self._request_json(
                session,
                "GET",
                f"{DATA_API_BASE}/car/status/{vehicle.id}/ev/battery",
                allow_error_codes=ALLOW_NO_DATA_CODES,
            )
            if battery:
                vehicle.ev_battery_percentage = battery.get("soc")
                self._update_last_updated(vehicle, battery.get("timestamp"))

            charging = await self._request_json(
                session,
                "GET",
                f"{DATA_API_BASE}/car/status/{vehicle.id}/ev/charging",
                allow_error_codes=ALLOW_NO_DATA_CODES,
            )
            if charging:
                vehicle.ev_battery_is_charging = charging.get("batteryCharge")
                vehicle.ev_battery_plugin = charging.get("batteryPlugin")
                if vehicle.ev_battery_percentage is None:
                    vehicle.ev_battery_percentage = charging.get("soc")
                self._update_last_updated(vehicle, charging.get("timestamp"))

        vehicle.low_fuel_warning = await self._get_warning_status(
            session, vehicle.id, "lowFuel"
        )
        vehicle.tire_pressure_warning = await self._get_warning_status(
            session, vehicle.id, "tirePressure"
        )
        vehicle.lamp_wire_warning = await self._get_warning_status(
            session, vehicle.id, "lampWire"
        )
        vehicle.smart_key_battery_warning = await self._get_warning_status(
            session, vehicle.id, "smartKeyBattery"
        )
        vehicle.washer_fluid_warning = await self._get_warning_status(
            session, vehicle.id, "washerFluid"
        )
        vehicle.brake_oil_warning = await self._get_warning_status(
            session, vehicle.id, "breakOil"
        )
        vehicle.engine_oil_warning = await self._get_warning_status(
            session, vehicle.id, "engineOil"
        )

    async def _get_warning_status(
        self, session: config_entry_oauth2_flow.OAuth2Session, vehicle_id: str, name: str
    ) -> bool | None:
        data = await self._request_json(
            session,
            "GET",
            f"{DATA_API_BASE}/car/status/warning/{vehicle_id}/{name}",
            allow_error_codes=ALLOW_NO_DATA_CODES,
        )
        if not data:
            return None
        return data.get("status")

    def _update_last_updated(self, vehicle: MyHyundaiVehicle, value: str | None) -> None:
        if not value:
            return
        parsed = self._parse_timestamp(value)
        if parsed is None:
            return
        if vehicle.last_updated_at is None or parsed > vehicle.last_updated_at:
            vehicle.last_updated_at = parsed

    def _parse_timestamp(self, value: str) -> datetime | None:
        try:
            parsed = datetime.strptime(value, "%Y%m%d%H%M%S")
        except ValueError:
            return None
        return parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

    async def _request_json(
        self,
        session: config_entry_oauth2_flow.OAuth2Session,
        method: str,
        url: str,
        allow_error_codes: set[str] | None = None,
    ) -> dict | None:
        resp = await session.async_request(method, url)
        data = await resp.json()
        if isinstance(data, dict) and "errCode" in data:
            err_code = data.get("errCode")
            err_msg = data.get("errMsg", "Unknown error")
            if allow_error_codes and err_code in allow_error_codes:
                _LOGGER.debug("Ignoring error %s: %s", err_code, err_msg)
                return None
            hint = CONSENT_REQUIRED_CODES.get(err_code)
            if hint:
                err_msg = f"{err_msg} ({hint})"
            raise HomeAssistantError(f"{err_code}: {err_msg}")
        return data

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
