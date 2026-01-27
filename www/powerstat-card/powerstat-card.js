import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class PowerStatCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
      }
      ha-card {
        background: #1c1c1e;
        color: white;
        border-radius: 20px;
        overflow: hidden;
        padding: 16px;
        position: relative;
      }
      .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
      }
      .room-name {
        font-size: 1.2rem;
        font-weight: 500;
        color: #8e8e93;
      }
      .brain-icon {
        width: 32px;
        height: 32px;
        background: #3a3a3c;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .main-display {
        text-align: center;
        margin-bottom: 24px;
      }
      .temp-value {
        font-size: 4rem;
        font-weight: 300;
        line-height: 1;
      }
      .temp-unit {
        font-size: 1.5rem;
        vertical-align: top;
        margin-left: 4px;
      }
      .status-text {
        font-size: 0.9rem;
        color: #30d158;
        margin-top: 8px;
      }
      .controls {
        display: flex;
        justify-content: center;
        gap: 12px;
      }
      .mode-chip {
        background: #2c2c2e;
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 0.8rem;
        cursor: pointer;
        transition: background 0.2s;
      }
      .mode-chip:hover {
        background: #3a3a3c;
      }
      .mode-chip.active {
        background: #007aff;
      }
    `;
  }

  render() {
    if (!this.hass || !this.config) return html``;

    const baseEntityId = this.config.entity;
    const statusEntity = this.hass.states[baseEntityId.replace('status', 'status')]; // Placeholder mapping
    const tempEntity = this.hass.states[baseEntityId.replace('status', 'effective_temperature')];
    const reasonEntity = this.hass.states[baseEntityId.replace('status', 'reason')];

    return html`
      <ha-card>
        <div class="header">
          <div class="room-name">Living Room</div>
          <div class="brain-icon">
            <img src="/local/powerstat-card/logo.png" style="width: 100%; height: 100%; border-radius: 50%;" />
          </div>
        </div>
        <div class="main-display">
          <div class="temp-value">
            ${tempEntity ? tempEntity.state : '--'}<span class="temp-unit">°C</span>
          </div>
          <div class="status-text">${reasonEntity ? reasonEntity.state : 'Idle'}</div>
        </div>
        <div class="controls">
          <div class="mode-chip active">Home</div>
          <div class="mode-chip">Away</div>
          <div class="mode-chip">Sleep</div>
          <div class="mode-chip">Auto</div>
        </div>
      </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define("powerstat-card", PowerStatCard);
