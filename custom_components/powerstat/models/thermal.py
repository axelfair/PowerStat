"""Thermal model for learning house heat/cool rates."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)

class ThermalModel:
    """Tracks heat/cool rates (°C/min) using exponential moving average."""

    def __init__(self, learning_rate: float = 0.1) -> None:
        """Initialize model."""
        self.learning_rate = learning_rate
        self.heat_rate = 0.0  # °C/min
        self.cool_rate = 0.0  # °C/min
        self.samples_heat = 0
        self.samples_cool = 0

    def update(self, mode: str, delta_temp: float, delta_time_mins: float) -> None:
        """Update the model with a new measurement."""
        if delta_time_mins <= 0:
            return

        rate = delta_temp / delta_time_mins

        if mode == "heat":
            if self.samples_heat == 0:
                self.heat_rate = rate
            else:
                self.heat_rate = (self.learning_rate * rate) + ((1 - self.learning_rate) * self.heat_rate)
            self.samples_heat += 1
            _LOGGER.debug("Updated heat_rate: %s", self.heat_rate)
            
        elif mode == "cool":
            # Cooling rate is typically negative (temp goes down), but we store absolute or signed?
            # Let's store signed rate (°C per minute).
            if self.samples_cool == 0:
                self.cool_rate = rate
            else:
                self.cool_rate = (self.learning_rate * rate) + ((1 - self.learning_rate) * self.cool_rate)
            self.samples_cool += 1
            _LOGGER.debug("Updated cool_rate: %s", self.cool_rate)

    def get_rates(self) -> dict[str, float]:
        """Return current estimated rates."""
        return {
            "heat_rate": round(self.heat_rate, 4),
            "cool_rate": round(self.cool_rate, 4),
            "samples_heat": self.samples_heat,
            "samples_cool": self.samples_cool,
        }
