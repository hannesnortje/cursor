import { litLoader, getLit } from '../lib/lit-loader.js';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'agents-status-card': AgentsStatusCard;
  }
}

interface Agent {
  agent_id: string;
  agent_type: string;
  name: string;
  status: string;
  last_activity: string;
  uptime: string;
  performance_metrics?: Record<string, any>;
  error_count?: number;
}

// Wait for Lit to be loaded, then define the component
getLit().then(async ({ LitElement, html, css }) => {

  export class AgentsStatusCard extends LitElement {
    static properties = {
      agents: { type: Array }
    };

    private agents: Agent[] = [];

    constructor() {
      super();
      this.agents = [];
    }

    render() {
      if (!this.agents || this.agents.length === 0) {
        return html`
        <div class="agents-card loading">
          <div class="card-header">
            <h3>🤖 Agents Status</h3>
            <div class="agents-count">0 Agents</div>
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

      const statusCounts = this.getStatusCounts();
      const operationalCount = statusCounts.operational || 0;
      const totalCount = this.agents.length;

      return html`
      <div class="agents-card">
        <div class="card-header">
          <h3>🤖 Agents Status</h3>
          <div class="agents-count">
            ${operationalCount}/${totalCount} Operational
          </div>
        </div>
        
        <div class="card-content">
          <div class="status-summary">
            <div class="status-item operational">
              <span class="status-icon">🟢</span>
              <span class="status-label">Operational</span>
              <span class="status-count">${statusCounts.operational || 0}</span>
            </div>
            
            <div class="status-item degraded">
              <span class="status-icon">🟡</span>
              <span class="status-label">Degraded</span>
              <span class="status-count">${statusCounts.degraded || 0}</span>
            </div>
            
            <div class="status-item down">
              <span class="status-icon">🔴</span>
              <span class="status-label">Down</span>
              <span class="status-count">${statusCounts.down || 0}</span>
            </div>
            
            <div class="status-item limited">
              <span class="status-icon">🟠</span>
              <span class="status-label">Limited</span>
              <span class="status-count">${statusCounts.limited || 0}</span>
            </div>
          </div>
          
          <div class="agents-list">
            ${this.agents.map(agent => this.renderAgentItem(agent))}
          </div>
          
          <div class="card-footer">
            <button class="view-all-btn" @click=${this.viewAllAgents}>
              View All Agents
            </button>
          </div>
        </div>
      </div>
    `;
    }

    private getStatusCounts(): Record<string, number> {
      const counts: Record<string, number> = {};

      this.agents.forEach(agent => {
        const status = agent.status.toLowerCase();
        counts[status] = (counts[status] || 0) + 1;
      });

      return counts;
    }

    private renderAgentItem(agent: Agent): any {
      const statusClass = this.getAgentStatusClass(agent.status);
      const statusIcon = this.getAgentStatusIcon(agent.status);
      const lastActivity = new Date(agent.last_activity).toLocaleTimeString();

      return html`
      <div class="agent-item ${statusClass}">
        <div class="agent-header">
          <div class="agent-info">
            <span class="agent-name">${agent.name}</span>
            <span class="agent-type">${agent.agent_type}</span>
          </div>
          <div class="agent-status">
            <span class="status-icon">${statusIcon}</span>
            <span class="status-text">${agent.status}</span>
          </div>
        </div>
        
        <div class="agent-details">
          <div class="detail-row">
            <span class="detail-label">ID:</span>
            <span class="detail-value">${agent.agent_id}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Uptime:</span>
            <span class="detail-value">${agent.uptime}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Last Activity:</span>
            <span class="detail-value">${lastActivity}</span>
          </div>
          
          ${agent.error_count && agent.error_count > 0 ? html`
            <div class="detail-row error">
              <span class="detail-label">Errors:</span>
              <span class="detail-value">${agent.error_count}</span>
            </div>
          ` : ''}
        </div>
      </div>
    `;
    }

    private getAgentStatusClass(status: string): string {
      switch (status.toLowerCase()) {
        case 'operational':
          return 'operational';
        case 'degraded':
          return 'degraded';
        case 'down':
          return 'down';
        case 'limited':
          return 'limited';
        default:
          return 'unknown';
      }
    }

    private getAgentStatusIcon(status: string): string {
      switch (status.toLowerCase()) {
        case 'operational':
          return '🟢';
        case 'degraded':
          return '🟡';
        case 'down':
          return '🔴';
        case 'limited':
          return '🟠';
        default:
          return '❓';
      }
    }

    private viewAllAgents(): void {
      // TODO: Implement view all agents modal
      console.log('View all agents clicked');
    }

    static styles = css`
    .agents-card {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 1rem;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(15px);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .agents-card::before {
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

    .agents-card:hover::before {
      left: 100%;
    }

    .agents-card:hover {
      transform: translateY(-4px) scale(1.02);
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
      border-color: rgba(255, 255, 255, 0.3);
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

    .agents-count {
      background: rgba(59, 130, 246, 0.2);
      color: #3b82f6;
      padding: 0.5rem 1rem;
      border-radius: 2rem;
      font-size: 0.875rem;
      font-weight: 500;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .status-summary {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .status-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      border-radius: 0.5rem;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .status-item.operational {
      border-color: rgba(16, 185, 129, 0.3);
      background: rgba(16, 185, 129, 0.1);
    }

    .status-item.degraded {
      border-color: rgba(245, 158, 11, 0.3);
      background: rgba(245, 158, 11, 0.1);
    }

    .status-item.down {
      border-color: rgba(239, 68, 68, 0.3);
      background: rgba(239, 68, 68, 0.1);
    }

    .status-item.limited {
      border-color: rgba(251, 146, 60, 0.3);
      background: rgba(251, 146, 60, 0.1);
    }

    .status-icon {
      font-size: 1.25rem;
    }

    .status-label {
      flex: 1;
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.8);
    }

    .status-count {
      font-weight: 600;
      color: white;
      font-size: 1.125rem;
    }

    .agents-list {
      max-height: 300px;
      overflow-y: auto;
      margin-bottom: 1.5rem;
    }

    .agent-item {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 0.75rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: all 0.2s ease;
    }

    .agent-item:hover {
      background: rgba(255, 255, 255, 0.08);
      transform: translateX(4px);
    }

    .agent-item.operational {
      border-color: rgba(16, 185, 129, 0.2);
    }

    .agent-item.degraded {
      border-color: rgba(245, 158, 11, 0.2);
    }

    .agent-item.down {
      border-color: rgba(239, 68, 68, 0.2);
    }

    .agent-item.limited {
      border-color: rgba(251, 146, 60, 0.2);
    }

    .agent-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }

    .agent-info {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .agent-name {
      font-weight: 600;
      color: white;
      font-size: 1rem;
    }

    .agent-type {
      font-size: 0.75rem;
      color: rgba(255, 255, 255, 0.6);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .agent-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .status-text {
      font-size: 0.875rem;
      font-weight: 500;
      text-transform: capitalize;
    }

    .agent-details {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.5rem;
    }

    .detail-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.875rem;
    }

    .detail-label {
      color: rgba(255, 255, 255, 0.7);
    }

    .detail-value {
      color: white;
      font-weight: 500;
    }

    .detail-row.error .detail-value {
      color: #ef4444;
    }

    .card-footer {
      text-align: center;
    }

    .view-all-btn {
      background: rgba(59, 130, 246, 0.2);
      color: #3b82f6;
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 0.75rem 1.5rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .view-all-btn:hover {
      background: rgba(59, 130, 246, 0.3);
      border-color: rgba(59, 130, 246, 0.4);
      transform: translateY(-1px);
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
      .agents-card {
        padding: 1rem;
      }

      .card-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }

      .status-summary {
        grid-template-columns: 1fr;
      }

      .agent-details {
        grid-template-columns: 1fr;
      }
    }
  `;
  }

  // Register the component
  customElements.define('agents-status-card', AgentsStatusCard);

  console.log('✅ Agents Status Card component registered successfully');

}).catch(error => {
  console.error('❌ Failed to load Lit 3 for Agents Status Card:', error);

  // Create a fallback component that shows the error
  class AgentsStatusCardError extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div style="
          padding: 1rem;
          background: rgba(244, 67, 54, 0.1);
          border: 1px solid #f44336;
          border-radius: 0.5rem;
          color: #f44336;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        ">
          <div style="font-weight: bold; margin-bottom: 0.5rem;">❌ Agents Status Card Failed</div>
          <div style="font-size: 0.9rem;">Error: ${error.message}</div>
          <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">
            Check console for more details
          </div>
        </div>
      `;
    }
  }

  customElements.define('agents-status-card', AgentsStatusCardError);
});
