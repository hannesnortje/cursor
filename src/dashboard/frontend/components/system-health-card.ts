import { litLoader, getLit } from '../lib/lit-loader.js';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'system-health-card': SystemHealthCard;
  }
}

interface SystemHealth {
  overall_status: string;
  timestamp: string;
  uptime: string;
  memory_usage: number;
  cpu_usage: number;
  disk_usage: number;
  active_connections: number;
  errors_count: number;
  warnings_count: number;
}

// Wait for Lit to be loaded, then define the componentngetLit().then(async ({ LitElement, html, css }) => {nnexport class SystemHealthCard extends LitElement {
  static properties = {
    systemHealth: { type: Object }
  };

  private systemHealth: SystemHealth | null = null;

  constructor() {
    super();
    this.systemHealth = null;
  }

  render() {
    if (!this.systemHealth) {
      return html`
        <div class="health-card loading">
          <div class="card-header">
            <h3>🏥 System Health</h3>
            <div class="status-badge loading">Loading...</div>
          </div>
          <div class="card-content">
            <div class="loading-placeholder">
              <div class="placeholder-line"></div>
              <div class="placeholder-line"></div>
              <div class="placeholder-line"></div>
            </div>
          </div>
        </div>
      `;
    }

    const statusClass = this.getStatusClass(this.systemHealth.overall_status);
    const statusIcon = this.getStatusIcon(this.systemHealth.overall_status);

    return html`
      <div class="health-card ${statusClass}">
        <div class="card-header">
          <h3>🏥 System Health</h3>
          <div class="status-badge ${statusClass}">
            ${statusIcon} ${this.systemHealth.overall_status}
          </div>
        </div>
        
        <div class="card-content">
          <div class="health-metrics">
            <div class="metric-row">
              <span class="metric-label">🕒 Uptime:</span>
              <span class="metric-value">${this.systemHealth.uptime}</span>
            </div>
            
            <div class="metric-row">
              <span class="metric-label">💾 Memory:</span>
              <span class="metric-value ${this.getUsageClass(this.systemHealth.memory_usage)}">
                ${this.systemHealth.memory_usage.toFixed(1)}%
              </span>
            </div>
            
            <div class="metric-row">
              <span class="metric-label">🖥️ CPU:</span>
              <span class="metric-value ${this.getUsageClass(this.systemHealth.cpu_usage)}">
                ${this.systemHealth.cpu_usage.toFixed(1)}%
              </span>
            </div>
            
            <div class="metric-row">
              <span class="metric-label">💿 Disk:</span>
              <span class="metric-value ${this.getUsageClass(this.systemHealth.disk_usage)}">
                ${this.systemHealth.disk_usage.toFixed(1)}%
              </span>
            </div>
            
            <div class="metric-row">
              <span class="metric-label">🔗 Connections:</span>
              <span class="metric-value">${this.systemHealth.active_connections}</span>
            </div>
          </div>
          
          <div class="health-alerts">
            ${this.systemHealth.errors_count > 0 ? html`
              <div class="alert error">
                ❌ ${this.systemHealth.errors_count} Error${this.systemHealth.errors_count > 1 ? 's' : ''}
              </div>
            ` : ''}
            
            ${this.systemHealth.warnings_count > 0 ? html`
              <div class="alert warning">
                ⚠️ ${this.systemHealth.warnings_count} Warning${this.systemHealth.warnings_count > 1 ? 's' : ''}
              </div>
            ` : ''}
            
            ${this.systemHealth.errors_count === 0 && this.systemHealth.warnings_count === 0 ? html`
              <div class="alert success">
                ✅ All systems operational
              </div>
            ` : ''}
          </div>
          
          <div class="last-updated">
            Last updated: ${new Date(this.systemHealth.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    `;
  }

  private getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'operational':
        return 'operational';
      case 'degraded':
        return 'degraded';
      case 'down':
        return 'down';
      default:
        return 'unknown';
    }
  }

  private getStatusIcon(status: string): string {
    switch (status.toLowerCase()) {
      case 'operational':
        return '🟢';
      case 'degraded':
        return '🟡';
      case 'down':
        return '🔴';
      default:
        return '❓';
    }
  }

  private getUsageClass(usage: number): string {
    if (usage < 50) return 'low';
    if (usage < 80) return 'medium';
    return 'high';
  }

  static styles = css`
    .health-card {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 1rem;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(15px);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .health-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.1), 
        transparent);
      transition: left 0.5s ease;
    }

    .health-card:hover::before {
      left: 100%;
    }

    .health-card:hover {
      transform: translateY(-4px) scale(1.02);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .health-card.operational {
      border-color: rgba(16, 185, 129, 0.3);
      background: rgba(16, 185, 129, 0.05);
    }

    .health-card.degraded {
      border-color: rgba(245, 158, 11, 0.3);
      background: rgba(245, 158, 11, 0.05);
    }

    .health-card.down {
      border-color: rgba(239, 68, 68, 0.3);
      background: rgba(239, 68, 68, 0.05);
    }

    .health-card.loading {
      border-color: rgba(107, 114, 128, 0.3);
      background: rgba(107, 114, 128, 0.05);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .card-header h3 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: white;
    }

    .status-badge {
      padding: 0.5rem 1rem;
      border-radius: 2rem;
      font-size: 0.875rem;
      font-weight: 500;
      text-transform: capitalize;
    }

    .status-badge.operational {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-badge.degraded {
      background: rgba(245, 158, 11, 0.2);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .status-badge.down {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .status-badge.loading {
      background: rgba(107, 114, 128, 0.2);
      color: #6b7280;
      border: 1px solid rgba(107, 114, 128, 0.3);
    }

    .health-metrics {
      margin-bottom: 1.5rem;
    }

    .metric-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .metric-row:last-child {
      border-bottom: none;
    }

    .metric-label {
      font-weight: 500;
      color: rgba(255, 255, 255, 0.8);
    }

    .metric-value {
      font-weight: 600;
      color: white;
    }

    .metric-value.low {
      color: #10b981;
    }

    .metric-value.medium {
      color: #f59e0b;
    }

    .metric-value.high {
      color: #ef4444;
    }

    .health-alerts {
      margin-bottom: 1rem;
    }

    .alert {
      padding: 0.75rem;
      border-radius: 0.5rem;
      margin-bottom: 0.5rem;
      font-size: 0.875rem;
      font-weight: 500;
    }

    .alert.error {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .alert.warning {
      background: rgba(245, 158, 11, 0.2);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .alert.success {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .last-updated {
      font-size: 0.75rem;
      color: rgba(255, 255, 255, 0.6);
      text-align: center;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .loading-placeholder {
      padding: 1rem 0;
    }

    .placeholder-line {
      height: 1rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 0.25rem;
      margin-bottom: 0.75rem;
      animation: pulse 1.5s infinite;
    }

    .placeholder-line:nth-child(2) {
      width: 80%;
    }

    .placeholder-line:nth-child(3) {
      width: 60%;
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
      .health-card {
        padding: 1rem;
      }

      .card-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }

      .metric-row {
        flex-direction: column;
        gap: 0.5rem;
        text-align: center;
      }
    }
  `;
}

// Register the component
customElements.define('system-health-card', SystemHealthCard);

console.log('✅ System Health Card component registered successfully');

}).catch(error => {
  console.error('❌ Failed to load Lit 3 for System Health Card:', error);
  
  // Create a fallback component that shows the error
  class SystemHealthCardError extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div style="
          padding: 1rem;
          background: rgba(244, 67, 54, 0.1);
          border: 1px solid #f44336;
          border-radius: 0.5rem;
          color: #f44336;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          text-align: center;
        ">
          <div style="font-weight: bold; margin-bottom: 0.5rem;">❌ System Health Card Failed</div>
          <div style="font-size: 0.9rem;">Error: ${error.message}</div>
          <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">
            Check console for more details
          </div>
        </div>
      `;
    }
  }
  
  customElements.define('system-health-card', SystemHealthCardError);
});
