"""Decision engine for PowerStat."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

class PowerStatPlanner:
    """The 'Brain' of the thermostat."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, snapshot: dict[str, Any]) -> None:
        """Initialize the planner."""
        self.hass = hass
        self.entry = entry
        self.snapshot = snapshot

    async def async_calculate_plan(self) -> dict[str, Any]:
        """Calculate the next HVAC plan based on current state."""
        # 1. Compute effective temp
        eff_temp = self._calculate_effective_temperature()
        
        if eff_temp is None:
            return {
                "hvac_mode": "off",
                "reason": "No temperature data available",
                "confidence": 0
            }

        # 2. Determine target band based on mode (Home/Away/Sleep)
        is_away = self.snapshot.get("is_away", False)
        is_sleep = self.snapshot.get("is_sleep", False)
        
        # Default targets (these will be moved to user-configurable settings later)
        target_temp = 21.0
        reason = "Mode: Home"
        
        if is_away:
            target_temp = 18.0
            reason = "Mode: Away (Eco)"
        elif is_sleep:
            target_temp = 19.0
            reason = "Mode: Sleep"
            
        hvac_mode = "off"
        if eff_temp < target_temp - 0.5:
            hvac_mode = "heat"
        elif eff_temp > target_temp + 0.5:
            hvac_mode = "cool"

        return {
            "effective_temp": eff_temp,
            "hvac_mode": hvac_mode,
            "target_temp": target_temp,
            "reason": reason,
            "confidence": 100
        }

    def _calculate_effective_temperature(self) -> float | None:
        """Weighted average of temperature sensors."""
        sensors = self.snapshot.get("sensors", {})
        presence = self.snapshot.get("presence", {})
        
        total_temp = 0.0
        total_weight = 0.0
        
        presence_boost = self.entry.data.get("presence_weight_boost", 2.0)

        for entity_id, state in sensors.items():
            try:
                temp = float(state)
                weight = 1.0
                
                # Check presence boost if presence entity is linked to this sensor (simplified for now)
                # In full version, we map sensors to Areas and presence to Areas.
                if presence.get(entity_id):
                    weight *= presence_boost
                
                total_temp += temp * weight
                total_weight += weight
            except (ValueError, TypeError):
                continue
                
        if total_weight == 0:
            return None
            
        return round(total_temp / total_weight, 1)
