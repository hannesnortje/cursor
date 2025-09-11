import { LitElement, css, html } from 'lit';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'dashboard-header': DashboardHeader;
  }
}

export class DashboardHeader extends LitElement {
  static properties = {
    websocketConnected: { type: Boolean }
  };

  private websocketConnected: boolean = false;

  constructor() {
    super();
    this.websocketConnected = false;
  }

  render() {
    return html`
      <header class="dashboard-header">
        <div class="header-content">
          <div class="header-left">
            <h1 class="dashboard-title">
              🤖 AI Agent System Dashboard
            </h1>
            <p class="dashboard-subtitle">
              Real-time monitoring and visualization
            </p>
          </div>

          <div class="header-right">
            <div class="connection-status">
              <div class="status-indicator ${this.websocketConnected ? 'connected' : 'disconnected'}">
                <span class="status-dot"></span>
                <span class="status-text">
                  ${this.websocketConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div class="status-details">
                <span class="status-label">WebSocket:</span>
                <span class="status-value ${this.websocketConnected ? 'connected' : 'disconnected'}">
                  ${this.websocketConnected ? '🟢 Active' : '🔴 Inactive'}
                </span>
              </div>
            </div>

            <div class="header-actions">
              <button class="action-btn refresh-btn" @click=${this.refreshPage}>
                🔄 Refresh
              </button>
              <button class="action-btn settings-btn" @click=${this.openSettings}>
                ⚙️ Settings
              </button>
            </div>
          </div>
        </div>
      </header>
    `;
  }

  private refreshPage(): void {
    window.location.reload();
  }

  private openSettings(): void {
    // Dispatch event to open settings panel
    this.dispatchEvent(new CustomEvent('open-settings', {
      bubbles: true,
      composed: true
    }));
  }

  static styles = css`
    .dashboard-header {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      padding: 1rem 2rem;
      position: relative;
      z-index: 10;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .dashboard-header::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg,
        rgba(255, 255, 255, 0.1) 0%,
        rgba(255, 255, 255, 0.05) 50%,
        rgba(255, 255, 255, 0.1) 100%);
      pointer-events: none;
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1400px;
      margin: 0 auto;
      position: relative;
      z-index: 1;
    }

    .header-left {
      flex: 1;
    }

    .dashboard-title {
      margin: 0;
      font-size: 2rem;
      font-weight: 700;
      background: linear-gradient(45deg, #fff, #e0e7ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .dashboard-subtitle {
      margin: 0.5rem 0 0 0;
      font-size: 1rem;
      opacity: 0.8;
      color: #e0e7ff;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 2rem;
    }

    .connection-status {
      text-align: right;
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.25rem;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      animation: pulse 2s infinite;
    }

    .status-indicator.disconnected .status-dot {
      background: #ef4444;
      animation: none;
    }

    .status-text {
      font-size: 0.875rem;
      font-weight: 500;
    }

    .status-details {
      font-size: 0.75rem;
      opacity: 0.7;
    }

    .status-label {
      margin-right: 0.5rem;
    }

    .status-value.connected {
      color: #10b981;
    }

    .status-value.disconnected {
      color: #ef4444;
    }

    .header-actions {
      display: flex;
      gap: 0.75rem;
    }

    .action-btn {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 0.875rem;
      transition: all 0.2s ease;
    }

    .action-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }

    .refresh-btn {
      background: rgba(59, 130, 246, 0.2);
      border-color: rgba(59, 130, 246, 0.3);
    }

    .refresh-btn:hover {
      background: rgba(59, 130, 246, 0.3);
      border-color: rgba(59, 130, 246, 0.4);
    }

    .settings-btn {
      background: rgba(107, 114, 128, 0.2);
      border-color: rgba(107, 114, 128, 0.3);
    }

    .settings-btn:hover {
      background: rgba(107, 114, 128, 0.3);
      border-color: rgba(107, 114, 128, 0.4);
    }

    @keyframes pulse {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.5;
      }
    }

    @media (max-width: 768px) {
      .dashboard-header {
        padding: 1rem;
      }

      .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }

      .header-right {
        flex-direction: column;
        gap: 1rem;
      }

      .dashboard-title {
        font-size: 1.5rem;
      }

      .dashboard-subtitle {
        font-size: 0.875rem;
      }
    }
  `;
}

customElements.define('dashboard-header', DashboardHeader);
