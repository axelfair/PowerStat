"""Preference model for learning user setpoint preferences."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)

class PreferenceModel:
    """Tracks user setpoint preferences based on context."""

    def __init__(self) -> None:
        """Initialize model."""
        # Key: (day_type, time_bucket, mode, occupied)
        # Value: {"heat": temp, "cool": temp, "count": int}
        self.preferences: dict[tuple, dict[str, Any]] = {}

    def get_context(self, now: datetime, mode: str, occupied: bool) -> tuple:
        """Get the context key for the current state."""
        day_type = "weekend" if now.weekday() >= 5 else "weekday"
        time_bucket = (now.hour * 60 + now.minute) // 30
        return (day_type, time_bucket, mode, occupied)

    def update_preference(self, context: tuple, hvac_mode: str, setpoint: float) -> None:
        """Update preference for a given context and hvac mode."""
        if context not in self.preferences:
            self.preferences[context] = {"heat": 21.0, "cool": 24.0, "count": 0}

        pref = self.preferences[context]
        count = pref["count"]
        
        # Learning rate decays as we get more samples
        learning_rate = 1.0 / (count + 1)
        
        if hvac_mode == "heat":
            pref["heat"] = (learning_rate * setpoint) + ((1 - learning_rate) * pref["heat"])
        elif hvac_mode == "cool":
            pref["cool"] = (learning_rate * setpoint) + ((1 - learning_rate) * pref["cool"])
            
        pref["count"] += 1
        _LOGGER.debug("Updated preference for context %s: %s", context, pref)

    def get_preference(self, context: tuple) -> dict[str, float]:
        """Get the preferred setpoints for a context."""
        return self.preferences.get(context, {"heat": 21.0, "cool": 24.0, "count": 0})
