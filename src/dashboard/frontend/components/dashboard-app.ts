import { litLoader, getLit } from '../lib/lit-loader.js';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'dashboard-app': DashboardApp;
  }
}

// Types for component properties
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

interface PerformanceMetrics {
  timestamp: string;
  cache_hit_rate: number;
  response_time_avg: number;
  throughput: number;
  active_agents: number;
  memory_usage: number;
  cpu_usage: number;
  queue_depth: number;
}

// Wait for Lit to be loaded, then define the component
getLit().then(async ({ LitElement, html, css }) => {
  
export class DashboardApp extends LitElement {
  static properties = {
    agents: { type: Array },
    systemHealth: { type: Object },
    performanceMetrics: { type: Object },
    websocketConnected: { type: Boolean },
    refreshInterval: { type: Number }
  };

  private agents: Agent[] = [];
  private systemHealth: SystemHealth | null = null;
  private performanceMetrics: PerformanceMetrics | null = null;
  private websocketConnected: boolean = false;
  private refreshInterval: number = 30000; // 30 seconds
  private websocket: WebSocket | null = null;
  private intervalId: number | null = null;

  constructor() {
    super();
    this.agents = [];
    this.systemHealth = null;
    this.performanceMetrics = null;
    this.websocketConnected = false;
    this.websocket = null;
    this.intervalId = null;
  }

  connectedCallback(): void {
    super.connectedCallback();
    console.log('🔌 Dashboard app component connected to DOM');
    try {
      this.initializeWebSocket();
      this.startDataRefresh();
      console.log('✅ Dashboard app initialization complete');
    } catch (error) {
      console.error('❌ Error initializing dashboard app:', error);
    }
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this.cleanup();
  }

  private cleanup(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  private initializeWebSocket(): void {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/api/websocket/ws`;
      
      this.websocket = new WebSocket(wsUrl);
      
      this.websocket.onopen = () => {
        console.log('🔌 WebSocket connected');
        this.websocketConnected = true;
        this.requestUpdate('websocketConnected');
      };
      
      this.websocket.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.websocket.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.websocketConnected = false;
        this.requestUpdate('websocketConnected');
      };
      
      this.websocket.onerror = (error: Event) => {
        console.error('WebSocket error:', error);
        this.websocketConnected = false;
        this.requestUpdate('websocketConnected');
      };
      
    } catch (error) {
      console.error('Failed to initialize WebSocket:', error);
      this.websocketConnected = false;
    }
  }

  private handleWebSocketMessage(data: any): void {
    switch (data.type) {
      case 'agent_update':
        this.updateAgentData(data.agents);
        break;
      case 'system_health_update':
        this.updateSystemHealth(data.health);
        break;
      case 'performance_update':
        this.updatePerformanceMetrics(data.metrics);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  private updateAgentData(agents: Agent[]): void {
    this.agents = agents;
    this.requestUpdate('agents');
  }

  private updateSystemHealth(health: SystemHealth): void {
    this.systemHealth = health;
    this.requestUpdate('systemHealth');
  }

  private updatePerformanceMetrics(metrics: PerformanceMetrics): void {
    this.performanceMetrics = metrics;
    this.requestUpdate('performanceMetrics');
  }

  private startDataRefresh(): void {
    // Initial data load
    this.refreshData();
    
    // Set up periodic refresh
    this.intervalId = window.setInterval(() => {
      this.refreshData();
    }, this.refreshInterval);
  }

  private async refreshData(): Promise<void> {
    try {
      await Promise.all([
        this.loadAgentStatus(),
        this.loadSystemHealth(),
        this.loadPerformanceMetrics()
      ]);
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
  }

  private async loadAgentStatus(): Promise<void> {
    try {
      const response = await fetch('/api/agents/status');
      if (response.ok) {
        const agents: Agent[] = await response.json();
        this.agents = agents;
      }
    } catch (error) {
      console.error('Failed to load agent status:', error);
    }
  }

  private async loadSystemHealth(): Promise<void> {
    try {
      const response = await fetch('/api/system/health');
      if (response.ok) {
        const health: SystemHealth = await response.json();
        this.systemHealth = health;
      }
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  }

  private async loadPerformanceMetrics(): Promise<void> {
    try {
      const response = await fetch('/api/performance/metrics');
      if (response.ok) {
        const metrics: PerformanceMetrics = await response.json();
        this.performanceMetrics = metrics;
      }
    } catch (error) {
      console.error('Failed to load performance metrics:', error);
    }
  }

  private pingWebSocket(): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({ type: 'ping' }));
    }
  }

  render() {
    try {
      return html`
        <div class="dashboard">
          <dashboard-header 
            .websocketConnected=${this.websocketConnected}>
          </dashboard-header>
          
          <main class="dashboard-content">
            <div class="dashboard-grid">
              <system-health-card 
                .systemHealth=${this.systemHealth}>
              </system-health-card>
              
              <agents-status-card 
                .agents=${this.agents}>
              </agents-status-card>
              
              <performance-card 
                .performanceMetrics=${this.performanceMetrics}>
              </performance-card>
              
              <quick-actions-card 
                @refresh-data=${this.refreshData}
                @ping-websocket=${this.pingWebSocket}>
              </quick-actions-card>
            </div>
          </main>
          
          <dashboard-footer></dashboard-footer>
        </div>
      `;
    } catch (error) {
      console.error('Error rendering dashboard app:', error);
      return html`
        <div class="dashboard">
          <div style="padding: 2rem; text-align: center;">
            <h1>🤖 AI Agent System Dashboard</h1>
            <p>Error loading dashboard components</p>
            <p style="color: red;">${(error as Error).message}</p>
            <button @click=${() => window.location.reload()}>🔄 Reload Page</button>
          </div>
        </div>
      `;
    }
  }

  static styles = css`
    .dashboard {
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      background-attachment: fixed;
      color: white;
      position: relative;
      overflow-x: hidden;
    }

    .dashboard::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
      pointer-events: none;
      z-index: 0;
    }

    .dashboard-content {
      padding: 2rem;
      position: relative;
      z-index: 1;
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      animation: fadeInUp 0.8s ease-out;
    }

    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes float {
      0%, 100% {
        transform: translateY(0px);
      }
      50% {
        transform: translateY(-10px);
      }
    }

    .dashboard-grid > * {
      animation: float 6s ease-in-out infinite;
    }

    .dashboard-grid > *:nth-child(2) {
      animation-delay: -2s;
    }

    .dashboard-grid > *:nth-child(3) {
      animation-delay: -4s;
    }

    .dashboard-grid > *:nth-child(4) {
      animation-delay: -6s;
    }

    @media (max-width: 768px) {
      .dashboard-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
        animation: none;
      }
      
      .dashboard-grid > * {
        animation: none;
      }
      
      .dashboard-content {
        padding: 1rem;
      }
    }

    @media (max-width: 480px) {
      .dashboard-content {
        padding: 0.5rem;
      }
    }
  `;
}

// Register the component
customElements.define('dashboard-app', DashboardApp);

console.log('✅ Dashboard App component registered successfully');

}).catch(error => {
  console.error('❌ Failed to load Lit 3 for Dashboard App:', error);
  
  // Create a fallback component that shows the error
  class DashboardAppError extends HTMLElement {
    connectedCallback() {
      this.innerHTML = `
        <div style="
          padding: 2rem;
          background: rgba(244, 67, 54, 0.1);
          border: 1px solid #f44336;
          border-radius: 0.5rem;
          color: #f44336;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          text-align: center;
        ">
          <div style="font-weight: bold; margin-bottom: 0.5rem; font-size: 1.2rem;">❌ Dashboard App Failed</div>
          <div style="font-size: 0.9rem;">Error: ${error.message}</div>
          <div style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.8;">
            Check console for more details
          </div>
        </div>
      `;
    }
  }
  
  customElements.define('dashboard-app', DashboardAppError);
});
