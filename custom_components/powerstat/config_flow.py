"""Config flow for PowerStat integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_CLIMATE_ENTITY,
    CONF_TEMP_SENSORS,
    CONF_HUMIDITY_SENSORS,
    CONF_WINDOW_SENSORS,
    CONF_PRESENCE_SENSORS,
    CONF_FANS,
    CONF_AWAY_ENTITY,
    CONF_SLEEP_ENTITY,
    CONF_DECISION_INTERVAL,
    CONF_MIN_ACTION_INTERVAL,
    CONF_TEMP_DEADBAND,
    CONF_MIN_SETPOINT_CHANGE,
    CONF_MIN_ON_TIME,
    CONF_MIN_OFF_TIME,
    CONF_OPEN_GRACE_PERIOD,
    CONF_CLOSE_STABILISE_PERIOD,
    CONF_MANUAL_HOLD_DURATION,
    CONF_OVERRIDE_WINDOW,
    CONF_PRESENCE_WEIGHT_BOOST,
    DEFAULT_DECISION_INTERVAL,
    DEFAULT_MIN_ACTION_INTERVAL,
    DEFAULT_TEMP_DEADBAND,
    DEFAULT_MIN_SETPOINT_CHANGE,
    DEFAULT_MIN_ON_TIME,
    DEFAULT_MIN_OFF_TIME,
    DEFAULT_OPEN_GRACE_PERIOD,
    DEFAULT_CLOSE_STABILISE_PERIOD,
    DEFAULT_MANUAL_HOLD_DURATION,
    DEFAULT_OVERRIDE_WINDOW,
    DEFAULT_PRESENCE_WEIGHT_BOOST,
)

class PowerStatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PowerStat."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - select primary climate."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_sensors()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate")
                    ),
                }
            ),
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: select temperature sensors."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_optional()

        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TEMP_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature", multiple=True)
                    ),
                }
            ),
        )

    async def async_step_optional(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: optional selections."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_advanced()

        return self.async_show_form(
            step_id="optional",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HUMIDITY_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="humidity", multiple=True)
                    ),
                    vol.Optional(CONF_WINDOW_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["binary_sensor", "sensor"], multiple=True)
                    ),
                    vol.Optional(CONF_PRESENCE_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["binary_sensor", "sensor"], multiple=True)
                    ),
                    vol.Optional(CONF_FANS): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="fan", multiple=True)
                    ),
                    vol.Optional(CONF_AWAY_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["person", "input_boolean", "alarm_control_panel", "input_select"])
                    ),
                    vol.Optional(CONF_SLEEP_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain=["binary_sensor", "input_boolean"])
                    ),
                }
            ),
        )

    async def async_step_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 4: advanced settings."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="PowerStat", data=self._data)

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_DECISION_INTERVAL, default=DEFAULT_DECISION_INTERVAL): vol.Coerce(int),
                    vol.Optional(CONF_MIN_ACTION_INTERVAL, default=DEFAULT_MIN_ACTION_INTERVAL): vol.Coerce(int),
                    vol.Optional(CONF_TEMP_DEADBAND, default=DEFAULT_TEMP_DEADBAND): vol.Coerce(float),
                    vol.Optional(CONF_MIN_SETPOINT_CHANGE, default=DEFAULT_MIN_SETPOINT_CHANGE): vol.Coerce(float),
                    vol.Optional(CONF_MIN_ON_TIME, default=DEFAULT_MIN_ON_TIME): vol.Coerce(int),
                    vol.Optional(CONF_MIN_OFF_TIME, default=DEFAULT_MIN_OFF_TIME): vol.Coerce(int),
                    vol.Optional(CONF_OPEN_GRACE_PERIOD, default=DEFAULT_OPEN_GRACE_PERIOD): vol.Coerce(int),
                    vol.Optional(CONF_CLOSE_STABILISE_PERIOD, default=DEFAULT_CLOSE_STABILISE_PERIOD): vol.Coerce(int),
                    vol.Optional(CONF_MANUAL_HOLD_DURATION, default=DEFAULT_MANUAL_HOLD_DURATION): vol.Coerce(int),
                    vol.Optional(CONF_OVERRIDE_WINDOW, default=DEFAULT_OVERRIDE_WINDOW): vol.Coerce(int),
                    vol.Optional(CONF_PRESENCE_WEIGHT_BOOST, default=DEFAULT_PRESENCE_WEIGHT_BOOST): vol.Coerce(float),
                }
            ),
        )
