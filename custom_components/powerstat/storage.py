"""Storage helper for PowerStat persistence."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

class PowerStatStorage:
    """Class to handle persistence of learning models."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self.store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def async_load(self) -> dict[str, Any] | None:
        """Load data from storage."""
        return await self.store.async_load()

    async def async_save(self, data: dict[str, Any]) -> None:
        """Save data to storage."""
        await self.store.async_save(data)
