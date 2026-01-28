"""Environmental awareness engine for PowerStat."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_OPEN

_LOGGER = logging.getLogger(__name__)

class EnvironmentMonitor:
    """Monitor environmental conditions for smart HVAC decisions."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, snapshot: dict[str, Any]) -> None:
        """Initialize the environment monitor."""
        self.hass = hass
        self.entry = entry
        self.snapshot = snapshot
        
    def get_outdoor_temp(self) -> float | None:
        """Get outdoor temperature from configured sensor."""
        from ..const import CONF_OUTDOOR_TEMP_SENSOR
        
        outdoor_sensor = self.entry.data.get(CONF_OUTDOOR_TEMP_SENSOR)
        if not outdoor_sensor:
            return None
            
        state = self.hass.states.get(outdoor_sensor)
        if not state:
            return None
            
        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid outdoor temp state: %s", state.state)
            return None
    
    def get_outdoor_humidity(self) -> float | None:
        """Get outdoor humidity from configured sensor."""
        from ..const import CONF_OUTDOOR_HUMIDITY_SENSOR
        
        humidity_sensor = self.entry.data.get(CONF_OUTDOOR_HUMIDITY_SENSOR)
        if not humidity_sensor:
            return None
            
        state = self.hass.states.get(humidity_sensor)
        if not state:
            return None
            
        try:
            return float(state.state)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid outdoor humidity state: %s", state.state)
            return None
    
    def get_forecast_data(self) -> dict[str, Any]:
        """Parse weather entity forecast for next 4-6 hours."""
        from ..const import CONF_WEATHER_ENTITY
        
        weather_entity = self.entry.data.get(CONF_WEATHER_ENTITY)
        if not weather_entity:
            return {}
            
        state = self.hass.states.get(weather_entity)
        if not state or not state.attributes:
            return {}
        
        forecast = state.attributes.get("forecast", [])
        if not forecast:
            return {}
        
        # Extract next 4 hours of data
        now = datetime.now()
        future_temps = []
        
        for item in forecast[:6]:  # Look at next 6 hourly entries
            try:
                item_time = datetime.fromisoformat(item.get("datetime", ""))
                if item_time > now and item_time <= now + timedelta(hours=4):
                    future_temps.append(item.get("temperature"))
            except (ValueError, TypeError):
                continue
        
        if not future_temps:
            return {}
        
        # Calculate trend
        temp_in_2h = future_temps[1] if len(future_temps) > 1 else future_temps[0]
        temp_in_4h = future_temps[-1]
        current_outdoor = self.get_outdoor_temp()
        
        if current_outdoor is None:
            current_outdoor = state.attributes.get("temperature")
        
        # Determine trending direction
        trend = "stable"
        if temp_in_4h > current_outdoor + 1.5:
            trend = "warming"
        elif temp_in_4h < current_outdoor - 1.5:
            trend = "cooling"
        
        return {
            "temp_in_2h": temp_in_2h,
            "temp_in_4h": temp_in_4h,
            "trending": trend,
            "forecast_available": True,
        }
    
    def get_open_windows(self) -> list[str]:
        """Get list of currently open windows/doors."""
        from ..const import CONF_WINDOW_SENSORS
        
        window_sensors = self.entry.data.get(CONF_WINDOW_SENSORS, [])
        open_windows = []
        
        for entity_id in window_sensors:
            state = self.hass.states.get(entity_id)
            if state and state.state in [STATE_ON, STATE_OPEN]:
                # Extract friendly name or use entity ID
                name = state.attributes.get("friendly_name", entity_id.split(".")[-1])
                open_windows.append(name)
        
        return open_windows
    
    def should_pause_for_openings(self, window_states: dict[str, dict]) -> tuple[bool, str | None]:
        """
        Check if HVAC should pause due to open windows/doors.
        
        Returns:
            (should_pause, reason_message)
        """
        from ..const import CONF_WINDOW_GRACE_PERIOD
        
        grace_period = self.entry.data.get(CONF_WINDOW_GRACE_PERIOD, 60)  # Default 60s
        
        for entity_id, window_data in window_states.items():
            if window_data.get("state") == "open":
                duration = window_data.get("duration", 0)
                if duration >= grace_period:
                    state = self.hass.states.get(entity_id)
                    name = state.attributes.get("friendly_name", entity_id.split(".")[-1]) if state else entity_id
                    return True, f"Paused: {name} open ({duration}s)"
        
        return False, None
    
    def is_free_cooling_available(self, indoor_temp: float, target_temp: float) -> bool:
        """Check if outdoor conditions allow free cooling (opening windows)."""
        from ..const import CONF_FREE_TEMP_DIFFERENTIAL
        
        outdoor_temp = self.get_outdoor_temp()
        if outdoor_temp is None:
            return False
        
        # Need cooling (indoor > target) AND outdoor is cooler by threshold
        differential = self.entry.data.get(CONF_FREE_TEMP_DIFFERENTIAL, 2.0)
        
        if indoor_temp > target_temp and outdoor_temp < indoor_temp - differential:
            return True
        
        return False
    
    def is_free_heating_available(self, indoor_temp: float, target_temp: float) -> bool:
        """Check if outdoor conditions allow free heating (solar gain)."""
        from ..const import CONF_FREE_TEMP_DIFFERENTIAL
        
        outdoor_temp = self.get_outdoor_temp()
        if outdoor_temp is None:
            return False
        
        # Need heating (indoor < target) AND outdoor is warmer by threshold
        differential = self.entry.data.get(CONF_FREE_TEMP_DIFFERENTIAL, 2.0)
        
        if indoor_temp < target_temp and outdoor_temp > indoor_temp + differential:
            return True
        
        return False
    
    def build_environment_snapshot(self) -> dict[str, Any]:
        """Build comprehensive environment snapshot for decision making."""
        outdoor_temp = self.get_outdoor_temp()
        outdoor_humidity = self.get_outdoor_humidity()
        forecast = self.get_forecast_data()
        open_windows = self.get_open_windows()
        
        return {
            "outdoor_temp": outdoor_temp,
            "outdoor_humidity": outdoor_humidity,
            "forecast": forecast,
            "open_windows": open_windows,
            "has_outdoor_data": outdoor_temp is not None,
            "has_forecast": forecast.get("forecast_available", False),
        }
