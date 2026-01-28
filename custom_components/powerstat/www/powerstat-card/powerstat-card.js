console.info("%c POWERSTAT-CARD %c v0.1.0 ", "color: white; background: #007aff; font-weight: 700;", "color: #007aff; background: white; font-weight: 700;");

class PowerStatCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const stateObj = hass.states[entityId];
    const status = stateObj ? stateObj.state : 'Unknown';
    
    // Attempt to find the temperature sensor
    const tempEntityId = entityId.replace('_status', '_effective_temperature');
    const tempObj = hass.states[tempEntityId];
    const temp = tempObj ? tempObj.state : '--';

    this.content.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="font-size: 1.2rem; font-weight: 500;">PowerStat</div>
        <img src="/local/powerstat-card/logo.png" style="width: 40px; height: 40px; border-radius: 50%;" />
      </div>
      <div style="margin: 20px 0; text-align: center;">
        <div style="font-size: 3rem; font-weight: 300;">${temp}°C</div>
        <div style="color: #30d158; font-size: 0.9rem;">${status}</div>
      </div>
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity (e.g., sensor.powerstat_status)');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }
}

if (!customElements.get('powerstat-card')) {
  customElements.define('powerstat-card', PowerStatCard);
}

// Add to the card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "powerstat-card",
  name: "PowerStat Card",
  preview: true,
  description: "The official PowerStat dashboard card"
});
