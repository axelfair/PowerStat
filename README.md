# PowerStat

Smart Adaptive Thermostat for Home Assistant (HACS).

## Features
- **Learning Brain**: Learns your house's thermal rates and your user preferences.
- **Weighted Comfort**: Multiple temp sensors weighted by room presence.
- **Safety First**: Built-in compressor short-cycle protection.
- **Explainable**: "Why" sensor explains every decision.
- **Beautiful UI**: Custom Lovelace card with "Brain" state indicators.

## Installation (Mental Simulation / HACS Custom Repository)

1. Ensure you have [HACS](https://hacs.xyz/) installed.
2. Go to HACS -> Integrations.
3. Click the three dots in the top right -> Custom repositories.
4. Add the URL of your GitHub repo and select "Integration" as the category.
5. Click "Add" and then install "PowerStat".
6. Restart Home Assistant.
7. Go to Settings -> Devices & Services -> Add Integration -> "PowerStat".

### Frontend Card
1. Go to HACS -> Frontend.
2. Click the three dots in the top right -> Custom repositories.
3. Add the URL of your GitHub repo and select "Lovelace" as the category.
4. Install the "PowerStat Card".

## Configuration
The config flow will guide you through:
1. Selecting your primary climate entity (e.g., Fujitsu via Intesis).
2. Selecting temperature sensors.
3. Optional humidity, presence, and window sensors.
4. Tuning safety settings (min on/off times).

## Disclaimer
This is for educational/experimental use. Use caution when allowing software to control HVAC hardware.
