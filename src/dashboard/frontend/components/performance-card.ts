import { LitElement, html, css } from 'lit';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'performance-card': PerformanceCard;
  }
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

export class PerformanceCard extends LitElement {
  static properties = {
    performanceMetrics: { type: Object }
  };

  private performanceMetrics: PerformanceMetrics | null = null;

  constructor() {
    super();
    this.performanceMetrics = null;
  }

  render() {
    if (!this.performanceMetrics) {
      return html`
        <div class="performance-card loading">
          <div class="card-header">
            <h3>📊 Performance Metrics</h3>
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

    const cacheEfficiency = this.getCacheEfficiency(this.performanceMetrics.cache_hit_rate);
    const responseTimeClass = this.getResponseTimeClass(this.performanceMetrics.response_time_avg);
    const throughputClass = this.getThroughputClass(this.performanceMetrics.throughput);

    return html`
      <div class="performance-card">
        <div class="card-header">
          <h3>📊 Performance Metrics</h3>
          <div class="status-badge ${cacheEfficiency}">
            ${this.getCacheIcon(this.performanceMetrics.cache_hit_rate)} ${cacheEfficiency}
          </div>
        </div>
        
        <div class="card-content">
          <div class="metrics-grid">
            <div class="metric-item cache">
              <div class="metric-header">
                <span class="metric-icon">💾</span>
                <span class="metric-label">Cache Hit Rate</span>
              </div>
              <div class="metric-value ${cacheEfficiency}">
                ${this.performanceMetrics.cache_hit_rate.toFixed(1)}%
              </div>
              <div class="metric-bar">
                <div class="metric-bar-fill ${cacheEfficiency}" 
                     style="width: ${this.performanceMetrics.cache_hit_rate}%"></div>
              </div>
            </div>
            
            <div class="metric-item response-time">
              <div class="metric-header">
                <span class="metric-icon">⚡</span>
                <span class="metric-label">Response Time</span>
              </div>
              <div class="metric-value ${responseTimeClass}">
                ${this.performanceMetrics.response_time_avg.toFixed(1)}ms
              </div>
              <div class="metric-bar">
                <div class="metric-bar-fill ${responseTimeClass}" 
                     style="width: ${Math.min(100, (this.performanceMetrics.response_time_avg / 500) * 100)}%"></div>
              </div>
            </div>
            
            <div class="metric-item throughput">
              <div class="metric-header">
                <span class="metric-icon">🚀</span>
                <span class="metric-label">Throughput</span>
              </div>
              <div class="metric-value ${throughputClass}">
                ${this.performanceMetrics.throughput.toFixed(1)} req/s
              </div>
              <div class="metric-bar">
                <div class="metric-bar-fill ${throughputClass}" 
                     style="width: ${Math.min(100, (this.performanceMetrics.throughput / 100) * 100)}%"></div>
              </div>
            </div>
            
            <div class="metric-item agents">
              <div class="metric-header">
                <span class="metric-icon">🤖</span>
                <span class="metric-label">Active Agents</span>
              </div>
              <div class="metric-value">
                ${this.performanceMetrics.active_agents}
              </div>
              <div class="metric-bar">
                <div class="metric-bar-fill" 
                     style="width: ${Math.min(100, (this.performanceMetrics.active_agents / 10) * 100)}%"></div>
              </div>
            </div>
          </div>
          
          <div class="system-metrics">
            <div class="system-metric">
              <span class="system-label">Memory Usage:</span>
              <span class="system-value ${this.getUsageClass(this.performanceMetrics.memory_usage)}">
                ${this.performanceMetrics.memory_usage.toFixed(1)}%
              </span>
            </div>
            
            <div class="system-metric">
              <span class="system-label">CPU Usage:</span>
              <span class="system-value ${this.getUsageClass(this.performanceMetrics.cpu_usage)}">
                ${this.performanceMetrics.cpu_usage.toFixed(1)}%
              </span>
            </div>
            
            <div class="system-metric">
              <span class="system-label">Queue Depth:</span>
              <span class="system-value ${this.getQueueClass(this.performanceMetrics.queue_depth)}">
                ${this.performanceMetrics.queue_depth}
              </span>
            </div>
          </div>
          
          <div class="performance-summary">
            <div class="summary-item">
              <span class="summary-label">Overall Performance:</span>
              <span class="summary-value ${this.getOverallPerformanceClass()}">
                ${this.getOverallPerformanceText()}
              </span>
            </div>
          </div>
          
          <div class="last-updated">
            Last updated: ${new Date(this.performanceMetrics.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    `;
  }

  private getCacheEfficiency(hitRate: number): string {
    if (hitRate >= 90) return 'excellent';
    if (hitRate >= 80) return 'good';
    if (hitRate >= 70) return 'fair';
    return 'poor';
  }

  private getCacheIcon(hitRate: number): string {
    if (hitRate >= 90) return '🟢';
    if (hitRate >= 80) return '🟡';
    if (hitRate >= 70) return '🟠';
    return '🔴';
  }

  private getResponseTimeClass(responseTime: number): string {
    if (responseTime < 100) return 'excellent';
    if (responseTime < 200) return 'good';
    if (responseTime < 300) return 'fair';
    return 'poor';
  }

  private getThroughputClass(throughput: number): string {
    if (throughput >= 80) return 'excellent';
    if (throughput >= 60) return 'good';
    if (throughput >= 40) return 'fair';
    return 'poor';
  }

  private getUsageClass(usage: number): string {
    if (usage < 50) return 'low';
    if (usage < 80) return 'medium';
    return 'high';
  }

  private getQueueClass(queueDepth: number): string {
    if (queueDepth === 0) return 'empty';
    if (queueDepth < 5) return 'low';
    if (queueDepth < 10) return 'medium';
    return 'high';
  }

  private getOverallPerformanceClass(): string {
    if (!this.performanceMetrics) return 'unknown';
    
    const cacheScore = this.performanceMetrics.cache_hit_rate >= 80 ? 1 : 0;
    const responseScore = this.performanceMetrics.response_time_avg < 200 ? 1 : 0;
    const throughputScore = this.performanceMetrics.throughput >= 60 ? 1 : 0;
    const totalScore = cacheScore + responseScore + throughputScore;
    
    if (totalScore >= 3) return 'excellent';
    if (totalScore >= 2) return 'good';
    if (totalScore >= 1) return 'fair';
    return 'poor';
  }

  private getOverallPerformanceText(): string {
    const performanceClass = this.getOverallPerformanceClass();
    switch (performanceClass) {
      case 'excellent':
        return '🟢 Excellent';
      case 'good':
        return '🟡 Good';
      case 'fair':
        return '🟠 Fair';
      case 'poor':
        return '🔴 Poor';
      default:
        return '❓ Unknown';
    }
  }

  static styles = css`
    .performance-card {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 1rem;
      padding: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(15px);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }

    .performance-card::before {
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

    .performance-card:hover::before {
      left: 100%;
    }

    .performance-card:hover {
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

    .status-badge {
      padding: 0.5rem 1rem;
      border-radius: 2rem;
      font-size: 0.875rem;
      font-weight: 500;
      text-transform: capitalize;
    }

    .status-badge.excellent {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-badge.good {
      background: rgba(59, 130, 246, 0.2);
      color: #3b82f6;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .status-badge.fair {
      background: rgba(245, 158, 11, 0.2);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .status-badge.poor {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .status-badge.loading {
      background: rgba(107, 114, 128, 0.2);
      color: #6b7280;
      border: 1px solid rgba(107, 114, 128, 0.3);
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .metric-item {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 0.5rem;
      padding: 1rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .metric-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
    }

    .metric-icon {
      font-size: 1.25rem;
    }

    .metric-label {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.8);
      font-weight: 500;
    }

    .metric-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: white;
      margin-bottom: 0.5rem;
    }

    .metric-value.excellent {
      color: #10b981;
    }

    .metric-value.good {
      color: #3b82f6;
    }

    .metric-value.fair {
      color: #f59e0b;
    }

    .metric-value.poor {
      color: #ef4444;
    }

    .metric-bar {
      height: 0.5rem;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 0.25rem;
      overflow: hidden;
    }

    .metric-bar-fill {
      height: 100%;
      border-radius: 0.25rem;
      transition: width 0.3s ease;
    }

    .metric-bar-fill.excellent {
      background: #10b981;
    }

    .metric-bar-fill.good {
      background: #3b82f6;
    }

    .metric-bar-fill.fair {
      background: #f59e0b;
    }

    .metric-bar-fill.poor {
      background: #ef4444;
    }

    .metric-bar-fill:not(.excellent):not(.good):not(.fair):not(.poor) {
      background: #6b7280;
    }

    .system-metrics {
      background: rgba(255, 255, 255, 0.05);
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 1.5rem;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .system-metric {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    .system-metric:last-child {
      border-bottom: none;
    }

    .system-label {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.8);
    }

    .system-value {
      font-weight: 600;
      color: white;
    }

    .system-value.low {
      color: #10b981;
    }

    .system-value.medium {
      color: #f59e0b;
    }

    .system-value.high {
      color: #ef4444;
    }

    .system-value.empty {
      color: #10b981;
    }

    .performance-summary {
      background: rgba(59, 130, 246, 0.1);
      border-radius: 0.5rem;
      padding: 1rem;
      margin-bottom: 1.5rem;
      border: 1px solid rgba(59, 130, 246, 0.2);
    }

    .summary-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .summary-label {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.8);
    }

    .summary-value {
      font-weight: 600;
      font-size: 1rem;
    }

    .summary-value.excellent {
      color: #10b981;
    }

    .summary-value.good {
      color: #3b82f6;
    }

    .summary-value.fair {
      color: #f59e0b;
    }

    .summary-value.poor {
      color: #ef4444;
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
      .performance-card {
        padding: 1rem;
      }

      .card-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }

      .metrics-grid {
        grid-template-columns: 1fr;
      }
    }
  `;
}

customElements.define('performance-card', PerformanceCard);
