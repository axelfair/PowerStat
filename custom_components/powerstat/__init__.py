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
    
    # 1. Copy the card to the www folder so it's accessible
    # This is more reliable than trying to register static paths across HA versions
    import shutil
    
    integration_dir = os.path.dirname(__file__)
    source_card_dir = os.path.join(integration_dir, "www", "powerstat-card")
    dest_card_dir = hass.config.path("www", "powerstat-card")
    
    try:
        # Create www directory if it doesn't exist
        os.makedirs(dest_card_dir, exist_ok=True)
        
        # Copy all files from source to destination
        if os.path.exists(source_card_dir):
            for item in os.listdir(source_card_dir):
                src = os.path.join(source_card_dir, item)
                dst = os.path.join(dest_card_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
            _LOGGER.info("Copied PowerStat card to %s", dest_card_dir)
        else:
            _LOGGER.warning("PowerStat card source directory not found: %s", source_card_dir)
    except Exception as err:
        _LOGGER.error("Failed to copy PowerStat card files: %s", err)
    
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
