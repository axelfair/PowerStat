"""DataUpdateCoordinator for PowerStat."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.const import STATE_ON

from .const import (
    DOMAIN,
    CONF_DECISION_INTERVAL,
    CONF_CLIMATE_ENTITY,
    CONF_TEMP_SENSORS,
    CONF_PRESENCE_SENSORS,
    CONF_AWAY_ENTITY,
    CONF_SLEEP_ENTITY,
    DEFAULT_DECISION_INTERVAL,
)
from .engine.planner import PowerStatPlanner
from .engine.rules import PowerStatRules

_LOGGER = logging.getLogger(__name__)

class PowerStatCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from sensors and triggering the planner."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        interval = entry.data.get(CONF_DECISION_INTERVAL, DEFAULT_DECISION_INTERVAL)
        self.rules = PowerStatRules(hass, entry.data)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        try:
            # 1. Gather state snapshot
            snapshot = self._gather_state_snapshot()
            
            # 2. Run Planner
            planner = PowerStatPlanner(self.hass, self.entry, snapshot)
            proposed_plan = await planner.async_calculate_plan()
            
            # 3. Validate with Rules
            final_plan = self.rules.validate_action(snapshot["climate"], proposed_plan)
            
            _LOGGER.debug("Planning cycle complete: %s", final_plan)
            
            # 4. Actuate if necessary
            await self._async_actuate(snapshot["climate"], final_plan)
            
            return {
                "snapshot": snapshot,
                "plan": final_plan,
            }
        except Exception as err:
            _LOGGER.exception("Planning cycle failed")
            raise UpdateFailed(f"Error communicating with sensors: {err}") from err

    async def _async_actuate(self, current_climate: dict[str, Any], plan: dict[str, Any]) -> None:
        """Send commands to the climate entity if they differ from current state."""
        climate_entity = self.entry.data.get(CONF_CLIMATE_ENTITY)
        
        target_mode = plan.get("hvac_mode")
        target_temp = plan.get("target_temp")

        # 1. Update HVAC Mode
        if target_mode and target_mode != current_climate.get("hvac_mode"):
            _LOGGER.info("Changing %s mode to %s", climate_entity, target_mode)
            await self.hass.services.async_call(
                "climate",
                "set_hvac_mode",
                {"entity_id": climate_entity, "hvac_mode": target_mode},
                blocking=True,
            )

        # 2. Update Temperature
        if target_temp and target_temp != current_climate.get("target_temp") and target_mode != "off":
            _LOGGER.info("Changing %s setpoint to %s", climate_entity, target_temp)
            await self.hass.services.async_call(
                "climate",
                "set_temperature",
                {"entity_id": climate_entity, "temperature": target_temp},
                blocking=True,
            )

    def _gather_state_snapshot(self) -> dict[str, Any]:
        """Gather current state of all configured entities."""
        climate_entity = self.entry.data.get(CONF_CLIMATE_ENTITY)
        temp_sensors = self.entry.data.get(CONF_TEMP_SENSORS, [])
        presence_sensors = self.entry.data.get(CONF_PRESENCE_SENSORS, [])
        away_entities = self.entry.data.get(CONF_AWAY_ENTITY, [])
        sleep_entities = self.entry.data.get(CONF_SLEEP_ENTITY, [])

        # Climate State
        climate_state = self.hass.states.get(climate_entity)
        climate_data = {
            "hvac_mode": climate_state.state if climate_state else "off",
            "target_temp": float(climate_state.attributes.get("temperature", 0)) if climate_state else 0.0,
            "last_changed": climate_state.last_changed if climate_state else None,
        }

        # Sensors
        sensor_data = {}
        for entity_id in temp_sensors:
            state = self.hass.states.get(entity_id)
            if state:
                sensor_data[entity_id] = state.state

        # Presence
        presence_data = {}
        for entity_id in presence_sensors:
            state = self.hass.states.get(entity_id)
            presence_data[entity_id] = (state.state == STATE_ON) if state else False

        # Consolidated Away State
        # If any person/device tracker is 'home', we are NOT away.
        # Otherwise, if any binary_sensor/input_boolean is 'on', we ARE away.
        any_person_home = False
        away_override = False
        
        for entity_id in away_entities:
            state = self.hass.states.get(entity_id)
            if not state:
                continue
            
            domain = entity_id.split(".")[0]
            if domain in ["person", "device_tracker"]:
                if state.state == "home":
                    any_person_home = True
            elif state.state == STATE_ON:
                away_override = True

        is_away = away_override or (len(away_entities) > 0 and not any_person_home)

        # Consolidated Sleep State
        is_sleep = False
        for entity_id in sleep_entities:
            state = self.hass.states.get(entity_id)
            if state and state.state == STATE_ON:
                is_sleep = True
                break

        # Environmental Data (outdoor conditions, forecast, windows)
        from .engine.environment import EnvironmentMonitor
        
        env_monitor = EnvironmentMonitor(self.hass, self.entry, {})
        env_snapshot = env_monitor.build_environment_snapshot()

        return {
            "climate": climate_data,
            "sensors": sensor_data,
            "presence": presence_data,
            "is_away": is_away,
            "is_sleep": is_sleep,
            "environment": env_snapshot,
        }
