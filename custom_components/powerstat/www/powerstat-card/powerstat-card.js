console.info("%c POWERSTAT-CARD %c v0.2.0 ", "color: white; background: #007aff; font-weight: 700;", "color: #007aff; background: white; font-weight: 700;");

class PowerStatCard extends HTMLElement {
  set hass(hass) {
    if (!this._initialized) {
      this._initialize();
    }

    const entityId = this.config.entity;
    const stateObj = hass.states[entityId];
    
    // Get all sensor data
    const status = stateObj ? stateObj.state : 'Unknown';
    const tempEntityId = entityId.replace('_status', '_effective_temperature');
    const reasonEntityId = entityId.replace('_status', '_reason');
    const confidenceEntityId = entityId.replace('_status', '_confidence');
    
    const tempObj = hass.states[tempEntityId];
    const reasonObj = hass.states[reasonEntityId];
    const confidenceObj = hass.states[confidenceEntityId];
    
    const temp = tempObj ? parseFloat(tempObj.state) : null;
    const reason = reasonObj ? reasonObj.state : 'Monitoring';
    const confidence = confidenceObj ? parseInt(confidenceObj.state) : 0;
    
    // Get plan data from attributes
    const plan = stateObj?.attributes?.plan || {};
    const targetTemp = plan.target_temp || 21;
    const hvacMode = plan.hvac_mode || 'off';
    
    this._render(temp, targetTemp, status, reason, confidence, hvacMode);
  }

  _initialize() {
    const card = document.createElement('ha-card');
    card.style.overflow = 'hidden';
    this.appendChild(card);
    this._card = card;
    this._initialized = true;
  }

  _render(temp, targetTemp, status, reason, confidence, hvacMode) {
    const statusColor = this._getStatusColor(status);
    const modeIcon = this._getModeIcon(hvacMode);
    
    this._card.innerHTML = `
      <style>
        .powerstat-container {
          padding: 20px;
          background: linear-gradient(135deg, #1c1c1e 0%, #2c2c2e 100%);
          color: #fff;
        }
        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 24px;
        }
        .logo {
          width: 48px;
          height: 48px;
          border-radius: 12px;
          padding: 8px;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
        }
        .brand {
          font-size: 1.4rem;
          font-weight: 600;
          letter-spacing: -0.5px;
        }
        .temp-display {
          text-align: center;
          margin: 32px 0;
          position: relative;
        }
        .temp-ring {
          width: 200px;
          height: 200px;
          margin: 0 auto;
          position: relative;
        }
        .temp-ring svg {
          transform: rotate(-90deg);
        }
        .temp-ring circle {
          fill: none;
          stroke-width: 8;
        }
        .temp-ring .ring-bg {
          stroke: rgba(255, 255, 255, 0.1);
        }
        .temp-ring .ring-progress {
          stroke: ${statusColor};
          stroke-linecap: round;
          transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease;
        }
        .temp-value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
        }
        .current-temp {
          font-size: 3.5rem;
          font-weight: 300;
          line-height: 1;
          margin-bottom: 4px;
        }
        .target-temp {
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.6);
          margin-top: 4px;
        }
        .mode-indicator {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 12px;
          background: ${statusColor}22;
          border: 1px solid ${statusColor};
          border-radius: 12px;
          font-size: 0.75rem;
          color: ${statusColor};
          margin-top: 8px;
        }
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          margin-top: 24px;
        }
        .stat-card {
          background: rgba(255, 255, 255, 0.08);
          border-radius: 12px;
          padding: 12px;
          backdrop-filter: blur(10px);
        }
        .stat-label {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.6);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 4px;
        }
        .stat-value {
          font-size: 1.25rem;
          font-weight: 600;
        }
        .reason-bar {
          margin-top: 20px;
          padding: 12px;
          background: rgba(255, 255, 255, 0.06);
          border-left: 3px solid ${statusColor};
          border-radius: 6px;
          font-size: 0.85rem;
          color: rgba(255, 255, 255, 0.9);
        }
        .confidence-bar {
          margin-top: 8px;
          height: 4px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
          overflow: hidden;
        }
        .confidence-fill {
          height: 100%;
          background: linear-gradient(90deg, ${statusColor}, ${statusColor}aa);
          width: ${confidence}%;
          transition: width 0.3s ease;
        }
      </style>
      
      <div class="powerstat-container">
        <div class="header">
          <div class="brand">PowerStat</div>
          <img src="/local/powerstat-card/logo.png" class="logo" />
        </div>
        
        <div class="temp-display">
          <div class="temp-ring">
            <svg width="200" height="200" viewBox="0 0 200 200">
              <circle class="ring-bg" cx="100" cy="100" r="90"></circle>
              <circle class="ring-progress" cx="100" cy="100" r="90" 
                      stroke-dasharray="${565}" 
                      stroke-dashoffset="${this._calculateRingOffset(temp, targetTemp)}"></circle>
            </svg>
            <div class="temp-value">
              <div class="current-temp">${temp !== null ? temp.toFixed(1) : '--'}°</div>
              <div class="target-temp">Target: ${targetTemp}°C</div>
              <div class="mode-indicator">
                <span>${modeIcon}</span>
                <span>${hvacMode.toUpperCase()}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Status</div>
            <div class="stat-value">${status}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Confidence</div>
            <div class="stat-value">${confidence}%</div>
          </div>
        </div>
        
        <div class="reason-bar">
          <strong>Decision:</strong> ${reason}
        </div>
        <div class="confidence-bar">
          <div class="confidence-fill"></div>
        </div>
      </div>
    `;
  }

  _calculateRingOffset(currentTemp, targetTemp) {
    if (currentTemp === null) return 565;
    
    // Calculate how close we are to target (0-100%)
    const range = 5; // ±5°C range
    const diff = Math.abs(currentTemp - targetTemp);
    const percentage = Math.max(0, Math.min(100, (1 - diff / range) * 100));
    
    // Convert to stroke-dashoffset (565 is full circle)
    return 565 - (565 * percentage / 100);
  }

  _getStatusColor(status) {
    const colors = {
      'acting': '#30d158',      // Green
      'suspended': '#ff9f0a',   // Orange
      'idle': '#64d2ff',        // Blue
      'learning': '#bf5af2',    // Purple
      'error': '#ff453a'        // Red
    };
    return colors[status.toLowerCase()] || '#8e8e93';
  }

  _getModeIcon(mode) {
    const icons = {
      'heat': '🔥',
      'cool': '❄️',
      'off': '⏸️',
      'auto': '🔄'
    };
    return icons[mode] || '•';
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity (e.g., sensor.powerstat_status)');
    }
    this.config = config;
  }

  getCardSize() {
    return 5;
  }
}

if (!customElements.get('powerstat-card')) {
  customElements.define('powerstat-card', PowerStatCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "powerstat-card",
  name: "PowerStat Card",
  preview: true,
  description: "Advanced AI thermostat control card"
});
