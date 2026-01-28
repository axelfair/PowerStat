"""Sensor platform for PowerStat."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_PLAN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PowerStat sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        PowerStatStatusSensor(coordinator),
        PowerStatEffectiveTempSensor(coordinator),
        PowerStatReasonSensor(coordinator),
        PowerStatConfidenceSensor(coordinator),
        PowerStatOutdoorTempSensor(coordinator),
        PowerStatOutdoorHumiditySensor(coordinator),
        PowerStatWindowStatusSensor(coordinator),
        PowerStatForecastTrendSensor(coordinator),
    ]
    
    async_add_entities(sensors)

class PowerStatBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for PowerStat."""

    def __init__(self, coordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{self.__class__.__name__}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "PowerStat",
            "manufacturer": "axelfair",
        }

class PowerStatStatusSensor(PowerStatBaseSensor):
    """Sensor that shows the current status of PowerStat (Idle/Thinking/Acting/etc)."""

    _attr_name = "PowerStat Status"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        plan = self.coordinator.data.get("plan")
        if plan and plan.get("blocked"):
            return "Suspended"
        return "Idle"

class PowerStatEffectiveTempSensor(PowerStatBaseSensor):
    """Sensor that shows the calculated weighted temperature."""

    _attr_name = "PowerStat Effective Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        plan = self.coordinator.data.get("plan")
        if plan:
            return plan.get("effective_temp")
        return None

class PowerStatReasonSensor(PowerStatBaseSensor):
    """Sensor that shows the reason for the last decision."""

    _attr_name = "PowerStat Reason"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        plan = self.coordinator.data.get("plan")
        if plan:
            return plan.get("reason", "Waiting")
        return "Initializing"

class PowerStatConfidenceSensor(PowerStatBaseSensor):
    """Sensor that shows the confidence score of the current plan."""

    _attr_name = "PowerStat Confidence"
    _attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        plan = self.coordinator.data.get("plan")
        if plan:
            return plan.get("confidence", 0)
        return 0

class PowerStatOutdoorTempSensor(PowerStatBaseSensor):
    """Sensor that shows outdoor temperature."""

    _attr_name = "PowerStat Outdoor Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        snapshot = self.coordinator.data.get("snapshot", {})
        env = snapshot.get("environment", {})
        return env.get("outdoor_temp")

class PowerStatOutdoorHumiditySensor(PowerStatBaseSensor):
    """Sensor that shows outdoor humidity."""

    _attr_name = "PowerStat Outdoor Humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        snapshot = self.coordinator.data.get("snapshot", {})
        env = snapshot.get("environment", {})
        return env.get("outdoor_humidity")

class PowerStatWindowStatusSensor(PowerStatBaseSensor):
    """Sensor that shows window/door status summary."""

    _attr_name = "PowerStat Window Status"
    _attr_icon = "mdi:window-open-variant"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        snapshot = self.coordinator.data.get("snapshot", {})
        env = snapshot.get("environment", {})
        open_windows = env.get("open_windows", [])
        
        if not open_windows:
            return "All Closed"
        
        count = len(open_windows)
        if count == 1:
            return f"1 Open: {open_windows[0]}"
        
        # Show first 2 window names if multiple
        preview = ", ".join(open_windows[:2])
        if count > 2:
            preview += f" +{count - 2} more"
        return f"{count} Open: {preview}"

class PowerStatForecastTrendSensor(PowerStatBaseSensor):
    """Sensor that shows weather forecast trend."""

    _attr_name = "PowerStat Forecast Trend"
    _attr_icon = "mdi:weather-partly-cloudy"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        snapshot = self.coordinator.data.get("snapshot", {})
        env = snapshot.get("environment", {})
        forecast = env.get("forecast", {})
        
        if not forecast.get("forecast_available"):
            return "No forecast data"
        
        trend = forecast.get("trending", "stable")
        temp_4h = forecast.get("temp_in_4h")
        
        if temp_4h:
            return f"{trend.capitalize()} (→{temp_4h}°C in 4h)"
        return trend.capitalize()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        snapshot = self.coordinator.data.get("snapshot", {})
        env = snapshot.get("environment", {})
        forecast = env.get("forecast", {})
        
        return {
            "temp_in_2h": forecast.get("temp_in_2h"),
            "temp_in_4h": forecast.get("temp_in_4h"),
            "trending": forecast.get("trending"),
        }
