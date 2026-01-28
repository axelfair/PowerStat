"""Constants for the PowerStat integration."""

DOMAIN = "powerstat"

# Config entries
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_TEMP_SENSORS = "temp_sensors"
CONF_HUMIDITY_SENSORS = "humidity_sensors"
CONF_WINDOW_SENSORS = "window_sensors"
CONF_PRESENCE_SENSORS = "presence_sensors"
CONF_FANS = "fans"
CONF_AWAY_ENTITY = "away_entity"
CONF_SLEEP_ENTITY = "sleep_entity"

# Environmental monitoring (optional)
CONF_OUTDOOR_TEMP_SENSOR = "outdoor_temp_sensor"
CONF_OUTDOOR_HUMIDITY_SENSOR = "outdoor_humidity_sensor"
CONF_WEATHER_ENTITY = "weather_entity"
CONF_FREE_TEMP_DIFFERENTIAL = "free_temp_differential"
CONF_WINDOW_GRACE_PERIOD = "window_grace_period"
CONF_EFFICIENCY_WARNINGS = "efficiency_warnings"

# Settings
CONF_DECISION_INTERVAL = "decision_interval"
CONF_MIN_ACTION_INTERVAL = "min_action_interval"
CONF_TEMP_DEADBAND = "temp_deadband"
CONF_MIN_SETPOINT_CHANGE = "min_setpoint_change"
CONF_MIN_ON_TIME = "min_on_time"
CONF_MIN_OFF_TIME = "min_off_time"
CONF_OPEN_GRACE_PERIOD = "open_grace_period"
CONF_CLOSE_STABILISE_PERIOD = "close_stabilise_period"
CONF_MANUAL_HOLD_DURATION = "manual_hold_duration"
CONF_OVERRIDE_WINDOW = "override_window"
CONF_PRESENCE_WEIGHT_BOOST = "presence_weight_boost"

# Defaults
DEFAULT_DECISION_INTERVAL = 120
DEFAULT_MIN_ACTION_INTERVAL = 300
DEFAULT_TEMP_DEADBAND = 0.3
DEFAULT_MIN_SETPOINT_CHANGE = 0.5
DEFAULT_MIN_ON_TIME = 10
DEFAULT_MIN_OFF_TIME = 8
DEFAULT_OPEN_GRACE_PERIOD = 60
DEFAULT_CLOSE_STABILISE_PERIOD = 120
DEFAULT_MANUAL_HOLD_DURATION = 60
DEFAULT_OVERRIDE_WINDOW = 20
DEFAULT_PRESENCE_WEIGHT_BOOST = 2.0
DEFAULT_FREE_TEMP_DIFFERENTIAL = 2.0
DEFAULT_WINDOW_GRACE_PERIOD = 60
DEFAULT_EFFICIENCY_WARNINGS = True

# Attributes / Internal constants
ATTR_REASON = "reason"
ATTR_CONFIDENCE = "confidence"
ATTR_PLAN = "plan"
