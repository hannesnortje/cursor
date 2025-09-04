import { LitElement, html, css } from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

// Type declarations for Lit 3
declare global {
  interface HTMLElementTagNameMap {
    'dashboard-footer': DashboardFooter;
  }
}

export class DashboardFooter extends LitElement {
  static properties = {};

  constructor() {
    super();
  }

  render() {
    const currentYear = new Date().getFullYear();
    
    return html`
      <footer class="dashboard-footer">
        <div class="footer-content">
          <div class="footer-left">
            <div class="footer-brand">
              <span class="brand-icon">🤖</span>
              <span class="brand-name">AI Agent System</span>
            </div>
            <div class="footer-description">
              Advanced AI agent orchestration and monitoring platform
            </div>
          </div>
          
          <div class="footer-center">
            <div class="footer-links">
              <a href="#" class="footer-link" @click=${this.openDocumentation}>
                📚 Documentation
              </a>
              <a href="#" class="footer-link" @click=${this.openSupport}>
                🆘 Support
              </a>
              <a href="#" class="footer-link" @click=${this.openGitHub}>
                🐙 GitHub
              </a>
            </div>
          </div>
          
          <div class="footer-right">
            <div class="footer-info">
              <div class="info-item">
                <span class="info-label">Version:</span>
                <span class="info-value">1.0.0</span>
              </div>
              <div class="info-item">
                <span class="info-label">Status:</span>
                <span class="info-value operational">🟢 Operational</span>
              </div>
              <div class="info-item">
                <span class="info-label">Uptime:</span>
                <span class="info-value" id="uptime-display">--</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <div class="footer-copyright">
            © ${currentYear} AI Agent System. All rights reserved.
          </div>
          <div class="footer-actions">
            <button class="footer-btn" @click=${this.refreshStatus}>
              🔄 Refresh Status
            </button>
            <button class="footer-btn" @click=${this.showSystemInfo}>
              ℹ️ System Info
            </button>
          </div>
        </div>
      </footer>
    `;
  }

  private openDocumentation(): void {
    // TODO: Implement documentation link
    console.log('📚 Documentation clicked');
    alert('Documentation will open in a new tab');
  }

  private openSupport(): void {
    // TODO: Implement support link
    console.log('🆘 Support clicked');
    alert('Support portal will open in a new tab');
  }

  private openGitHub(): void {
    // TODO: Implement GitHub link
    console.log('🐙 GitHub clicked');
    alert('GitHub repository will open in a new tab');
  }

  private refreshStatus(): void {
    const uptimeElement = this.shadowRoot?.getElementById('uptime-display');
    
    if (uptimeElement) {
      uptimeElement.textContent = 'Refreshing...';
      
      // Simulate status refresh
      setTimeout(() => {
        if (uptimeElement) {
          const uptime = this.calculateUptime();
          uptimeElement.textContent = uptime;
        }
      }, 1000);
    }
    
    console.log('🔄 Status refresh initiated');
  }

  private showSystemInfo(): void {
    const systemInfo = {
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      language: navigator.language,
      cookieEnabled: navigator.cookieEnabled,
      onLine: navigator.onLine,
      timestamp: new Date().toISOString()
    };
    
    console.log('ℹ️ System Info:', systemInfo);
    
    // Show system info in a formatted way
    const infoText = Object.entries(systemInfo)
      .map(([key, value]) => `${key}: ${value}`)
      .join('\n');
    
    alert(`System Information:\n\n${infoText}`);
  }

  private calculateUptime(): string {
    // Simulate uptime calculation
    const startTime = new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000); // Random start time within 24h
    const now = new Date();
    const diff = now.getTime() - startTime.getTime();
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  }

  static styles = css`
    .dashboard-footer {
      background: rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(10px);
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding: 2rem 0 1rem 0;
      margin-top: 3rem;
      position: relative;
    }

    .dashboard-footer::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, 
        transparent, 
        rgba(255, 255, 255, 0.3), 
        transparent);
    }

    .footer-content {
      display: grid;
      grid-template-columns: 2fr 1fr 2fr;
      gap: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      padding: 0 2rem;
    }

    .footer-left {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .footer-brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .brand-icon {
      font-size: 1.5rem;
    }

    .brand-name {
      font-size: 1.25rem;
      font-weight: 700;
      color: white;
    }

    .footer-description {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.7);
      line-height: 1.5;
    }

    .footer-center {
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .footer-links {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .footer-link {
      color: rgba(255, 255, 255, 0.8);
      text-decoration: none;
      font-size: 0.875rem;
      transition: color 0.2s ease;
      cursor: pointer;
    }

    .footer-link:hover {
      color: white;
    }

    .footer-right {
      display: flex;
      justify-content: flex-end;
      align-items: flex-start;
    }

    .footer-info {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      text-align: right;
    }

    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      font-size: 0.875rem;
    }

    .info-label {
      color: rgba(255, 255, 255, 0.7);
    }

    .info-value {
      color: white;
      font-weight: 500;
    }

    .info-value.operational {
      color: #10b981;
    }

    .footer-bottom {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1400px;
      margin: 0 auto;
      padding: 1.5rem 2rem 0 2rem;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .footer-copyright {
      font-size: 0.875rem;
      color: rgba(255, 255, 255, 0.6);
    }

    .footer-actions {
      display: flex;
      gap: 0.75rem;
    }

    .footer-btn {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 0.5rem;
      cursor: pointer;
      font-size: 0.875rem;
      transition: all 0.2s ease;
    }

    .footer-btn:hover {
      background: rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-1px);
    }

    @media (max-width: 768px) {
      .footer-content {
        grid-template-columns: 1fr;
        gap: 1.5rem;
        text-align: center;
      }

      .footer-right {
        justify-content: center;
      }

      .footer-info {
        text-align: center;
      }

      .footer-bottom {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }
    }
  `;
}

customElements.define('dashboard-footer', DashboardFooter);
