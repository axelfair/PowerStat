"""The PowerStat integration."""
from __future__ import annotations

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PowerStatCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PowerStat from a config entry."""
    coordinator = PowerStatCoordinator(hass, entry)
    
    # 1. Register the static path for the card
    # This makes the card available at /powerstat/powerstat-card.js
    # We use the integration's directory to ensure it works even on HA Green/OS
    integration_dir = os.path.dirname(__file__)
    card_path = os.path.join(integration_dir, "www", "powerstat-card")
    
    try:
        hass.http.register_static_path(
            "/powerstat",
            card_path,
            True,
        )
        _LOGGER.debug("Registered static path /powerstat for %s", card_path)
    except ValueError:
        _LOGGER.debug("Static path /powerstat already registered")
    
    # 2. Initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
