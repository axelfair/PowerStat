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
from homeassistant.const import UnitOfTemperature
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
