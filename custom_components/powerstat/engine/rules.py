"""Safety rules and constraints for PowerStat HVAC control."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from ..const import (
    CONF_MIN_ON_TIME,
    CONF_MIN_OFF_TIME,
    DEFAULT_MIN_ON_TIME,
    DEFAULT_MIN_OFF_TIME,
)

_LOGGER = logging.getLogger(__name__)

class PowerStatRules:
    """Class to handle safety rules like compressor protection."""

    def __init__(self, hass: HomeAssistant, config: dict[str, Any]) -> None:
        """Initialize rules."""
        self.hass = hass
        self.config = config
        self.min_on_time = timedelta(minutes=config.get(CONF_MIN_ON_TIME, DEFAULT_MIN_ON_TIME))
        self.min_off_time = timedelta(minutes=config.get(CONF_MIN_OFF_TIME, DEFAULT_MIN_OFF_TIME))

    def validate_action(
        self, 
        current_state: dict[str, Any], 
        proposed_action: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate a proposed HVAC action against safety rules.
        Returns a modified action or the original if safe.
        """
        now = dt_util.now()
        last_changed = current_state.get("last_changed")
        current_hvac_mode = current_state.get("hvac_mode")
        proposed_hvac_mode = proposed_action.get("hvac_mode")

        if not last_changed:
            return proposed_action

        time_since_change = now - last_changed

        # Compressor Short-Cycle Protection
        if current_hvac_mode != "off" and proposed_hvac_mode == "off":
            # Attempting to turn OFF
            if time_since_change < self.min_on_time:
                _LOGGER.debug(
                    "Short-cycle protection: Holding %s for another %s",
                    current_hvac_mode,
                    self.min_on_time - time_since_change
                )
                return {
                    **proposed_action,
                    "hvac_mode": current_hvac_mode,
                    "target_temp": current_state.get("target_temp"),
                    "reason": f"Waiting (min on-time: {self.min_on_time.total_seconds()/60}m)",
                    "blocked": True
                }

        if current_hvac_mode == "off" and proposed_hvac_mode != "off":
            # Attempting to turn ON
            if time_since_change < self.min_off_time:
                _LOGGER.debug(
                    "Short-cycle protection: Holding OFF for another %s",
                    self.min_off_time - time_since_change
                )
                return {
                    **proposed_action,
                    "hvac_mode": "off",
                    "reason": f"Waiting (min off-time: {self.min_off_time.total_seconds()/60}m)",
                    "blocked": True
                }

        return proposed_action
