class PowerStatCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      card.header = 'PowerStat';
      this.content = document.createElement('div');
      this.content.style.padding = '16px';
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];
    const stateStr = state ? state.state : 'unavailable';

    this.content.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <span>Status: ${stateStr}</span>
        <img src="/local/powerstat-card/logo.png" style="width: 50px; height: 50px; border-radius: 50%;" />
      </div>
      <div style="margin-top: 10px; color: #8e8e93;">
        Effective Temp: ${hass.states[entityId.replace('status', 'effective_temperature')]?.state || '--'}°C
      </div>
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('powerstat-card', PowerStatCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "powerstat-card",
  name: "PowerStat Card",
  preview: true,
  description: "The official PowerStat dashboard card"
});
