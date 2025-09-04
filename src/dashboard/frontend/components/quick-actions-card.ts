import { LitElement, html, css } from 'lit';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'quick-actions-card': QuickActionsCard;
  }
}

export class QuickActionsCard extends LitElement {
  static properties = {};

  constructor() {
    super();
  }

  render() {
    return html`
      <div class="actions-card">
        <div class="card-header">
          <h3>⚡ Quick Actions</h3>
          <div class="actions-subtitle">Common dashboard operations</div>
        </div>
        
        <div class="card-content">
          <div class="actions-grid">
            <button class="action-btn primary" @click=${this.refreshData}>
              <span class="action-icon">🔄</span>
              <span class="action-label">Refresh Data</span>
              <span class="action-description">Update all dashboard metrics</span>
            </button>
            
            <button class="action-btn secondary" @click=${this.pingWebSocket}>
              <span class="action-icon">📡</span>
              <span class="action-label">Ping WebSocket</span>
              <span class="action-description">Test real-time connection</span>
            </button>
            
            <button class="action-btn secondary" @click=${this.exportData}>
              <span class="action-icon">📊</span>
              <span class="action-label">Export Data</span>
              <span class="action-description">Download metrics as CSV</span>
            </button>
            
            <button class="action-btn secondary" @click=${this.openSettings}>
              <span class="action-icon">⚙️</span>
              <span class="action-label">Settings</span>
              <span class="action-description">Configure dashboard options</span>
            </button>
            
            <button class="action-btn secondary" @click=${this.viewLogs}>
              <span class="action-icon">📋</span>
              <span class="action-label">View Logs</span>
              <span class="action-description">System and error logs</span>
            </button>
            
            <button class="action-btn secondary" @click=${this.restartSystem}>
              <span class="action-icon">🔄</span>
              <span class="action-label">Restart System</span>
              <span class="action-description">Restart AI Agent System</span>
            </button>
          </div>
          
          <div class="quick-stats">
            <div class="stat-item">
              <span class="stat-icon">🕒</span>
              <span class="stat-label">Last Refresh</span>
              <span class="stat-value" id="last-refresh">Never</span>
            </div>
            
            <div class="stat-item">
              <span class="stat-icon">📡</span>
              <span class="stat-label">WebSocket Status</span>
              <span class="stat-value" id="ws-status">Unknown</span>
            </div>
            
            <div class="stat-item">
              <span class="stat-icon">⚡</span>
              <span class="stat-label">Response Time</span>
              <span class="stat-value" id="response-time">--</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private refreshData(): void {
    const lastRefreshElement = this.shadowRoot?.getElementById('last-refresh');
    const responseTimeElement = this.shadowRoot?.getElementById('response-time');
    
    if (lastRefreshElement) {
      lastRefreshElement.textContent = new Date().toLocaleTimeString();
    }
    
    if (responseTimeElement) {
      responseTimeElement.textContent = 'Refreshing...';
      
      // Simulate API call
      setTimeout(() => {
        if (responseTimeElement) {
          const responseTime = Math.random() * 200 + 50; // 50-250ms
          responseTimeElement.textContent = `${responseTime.toFixed(0)}ms`;
        }
      }, 1000);
    }
    
    // Dispatch custom event for parent component
    this.dispatchEvent(new CustomEvent('refresh-data', {
      detail: { timestamp: new Date().toISOString() },
      bubbles: true,
      composed: true
    }));
    
    console.log('🔄 Data refresh initiated');
  }

  private pingWebSocket(): void {
    const wsStatusElement = this.shadowRoot?.getElementById('ws-status');
    
    if (wsStatusElement) {
      wsStatusElement.textContent = 'Pinging...';
      wsStatusElement.style.color = '#f59e0b';
    }
    
    // Simulate WebSocket ping
    setTimeout(() => {
      if (wsStatusElement) {
        wsStatusElement.textContent = 'Connected';
        wsStatusElement.style.color = '#10b981';
      }
    }, 500);
    
    // Dispatch custom event for parent component
    this.dispatchEvent(new CustomEvent('ping-websocket', {
      detail: { timestamp: new Date().toISOString() },
      bubbles: true,
      composed: true
    }));
    
    console.log('📡 WebSocket ping sent');
  }

  private exportData(): void {
    // Simulate data export
    const data = {
      timestamp: new Date().toISOString(),
      agents: [],
      systemHealth: {},
      performanceMetrics: {}
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('📊 Data exported successfully');
  }

  private openSettings(): void {
    // TODO: Implement settings modal
    console.log('⚙️ Settings clicked');
    
    // Show a simple alert for now
    alert('Settings functionality coming soon!');
  }

  private viewLogs(): void {
    // TODO: Implement logs viewer
    console.log('📋 View logs clicked');
    
    // Show a simple alert for now
    alert('Logs viewer functionality coming soon!');
  }

  private restartSystem(): void {
    // Confirm before restarting
    if (confirm('Are you sure you want to restart the AI Agent System? This will temporarily disconnect all agents.')) {
      console.log('🔄 System restart initiated');
      
      // Show restarting status
      const restartBtn = this.shadowRoot?.querySelector('.action-btn:last-child .action-label') as HTMLElement;
      if (restartBtn) {
        const originalText = restartBtn.textContent;
        restartBtn.textContent = 'Restarting...';
        restartBtn.style.color = '#f59e0b';
        
        // Simulate restart process
        setTimeout(() => {
          if (restartBtn) {
            restartBtn.textContent = originalText;
            restartBtn.style.color = '';
          }
        }, 3000);
      }
    }
  }

  static styles = css`
    .actions-card {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 1rem;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(15px);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .actions-card::before {
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

    .actions-card:hover::before {
      left: 100%;
    }

    .actions-card:hover {
      transform: translateY(-4px) scale(1.02);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .card-header {
      text-align: center;
      margin-bottom: 1.5rem;
    }

    .card-header h3 {
      margin: 0 0 0.5rem 0;
      font-size: 1.25rem;
      font-weight: 600;
      color: white;
    }

    .actions-subtitle {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.7);
    }

    .actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .action-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 0.75rem;
      padding: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: left;
      color: white;
      font-family: inherit;
    }

    .action-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-2px);
    }

    .action-btn.primary {
      background: rgba(59, 130, 246, 0.2);
      border-color: rgba(59, 130, 246, 0.3);
    }

    .action-btn.primary:hover {
      background: rgba(59, 130, 246, 0.3);
      border-color: rgba(59, 130, 246, 0.4);
    }

    .action-btn.secondary {
      background: rgba(107, 114, 128, 0.2);
      border-color: rgba(107, 114, 128, 0.3);
    }

    .action-btn.secondary:hover {
      background: rgba(107, 114, 128, 0.3);
      border-color: rgba(107, 114, 128, 0.4);
    }

    .action-icon {
      display: block;
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
    }

    .action-label {
      display: block;
      font-weight: 600;
      font-size: 0.875rem;
      margin-bottom: 0.25rem;
    }

    .action-description {
      display: block;
      font-size: 0.75rem;
      color: rgba(255, 255, 255, 0.7);
      line-height: 1.3;
    }

    .quick-stats {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 0.75rem;
      padding: 1rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .stat-item:last-child {
      border-bottom: none;
    }

    .stat-icon {
      font-size: 1rem;
      width: 1.5rem;
      text-align: center;
    }

    .stat-label {
      flex: 1;
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.8);
    }

    .stat-value {
      font-weight: 600;
      color: white;
      font-size: 0.875rem;
    }

    @media (max-width: 768px) {
      .actions-card {
        padding: 1rem;
      }

      .actions-grid {
        grid-template-columns: 1fr;
      }

      .action-btn {
        text-align: center;
      }

      .action-icon {
        margin-bottom: 0.75rem;
      }
    }
  `;
}

customElements.define('quick-actions-card', QuickActionsCard);
