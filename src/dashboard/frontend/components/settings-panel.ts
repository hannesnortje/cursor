import { LitElement, css, html } from 'lit';

// Type declarations for Lit 3
declare global {
    interface HTMLElementTagNameMap {
        'settings-panel': SettingsPanel;
    }
}

interface CoordinatorSettings {
    coordinatorType: 'fast' | 'memory-enhanced' | 'auto';
    autoSwitchThreshold: number;
    responseTimeoutMs: number;
    enableMemoryLearning: boolean;
    debugMode: boolean;
}

export class SettingsPanel extends LitElement {
    static properties = {
        isVisible: { type: Boolean },
        settings: { type: Object }
    };

    isVisible = false;
    settings: CoordinatorSettings = {
        coordinatorType: 'memory-enhanced', // Current default after our switch
        autoSwitchThreshold: 5000, // ms - switch to fast if response time > threshold
        responseTimeoutMs: 10000,
        enableMemoryLearning: true,
        debugMode: false
    };

    static styles = css`
    .settings-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: flex;
      justify-content: center;
      align-items: center;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }

    .settings-overlay.visible {
      opacity: 1;
      pointer-events: all;
    }

    .settings-panel {
      background: linear-gradient(145deg, #1a1a2e, #16213e);
      border: 1px solid #0f3460;
      border-radius: 16px;
      padding: 2rem;
      width: 90%;
      max-width: 600px;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      transform: scale(0.8);
      transition: transform 0.3s ease;
    }

    .settings-overlay.visible .settings-panel {
      transform: scale(1);
    }

    .settings-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #0f3460;
    }

    .settings-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #ffffff;
      margin: 0;
    }

    .close-button {
      background: none;
      border: none;
      color: #ffffff;
      font-size: 1.5rem;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 8px;
      transition: background-color 0.2s ease;
    }

    .close-button:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }

    .setting-group {
      margin-bottom: 2rem;
    }

    .setting-label {
      display: block;
      color: #e2e8f0;
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .setting-description {
      color: #94a3b8;
      font-size: 0.875rem;
      margin-bottom: 1rem;
    }

    .coordinator-type-selector {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .coordinator-option {
      border: 2px solid #0f3460;
      border-radius: 12px;
      padding: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
      background: transparent;
      color: #e2e8f0;
    }

    .coordinator-option.selected {
      border-color: #3b82f6;
      background: rgba(59, 130, 246, 0.1);
    }

    .coordinator-option:hover {
      border-color: #60a5fa;
      background: rgba(96, 165, 250, 0.05);
    }

    .option-title {
      font-weight: 600;
      margin-bottom: 0.5rem;
    }

    .option-subtitle {
      font-size: 0.875rem;
      color: #94a3b8;
      margin-bottom: 0.5rem;
    }

    .option-performance {
      font-size: 0.75rem;
      color: #60a5fa;
    }

    .setting-control {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .setting-input {
      background: rgba(15, 52, 96, 0.5);
      border: 1px solid #0f3460;
      border-radius: 8px;
      padding: 0.75rem;
      color: #ffffff;
      flex: 1;
    }

    .setting-input:focus {
      outline: none;
      border-color: #3b82f6;
    }

    .setting-toggle {
      position: relative;
      width: 48px;
      height: 24px;
      background: #374151;
      border-radius: 12px;
      cursor: pointer;
      transition: background-color 0.2s ease;
    }

    .setting-toggle.enabled {
      background: #3b82f6;
    }

    .toggle-switch {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 20px;
      height: 20px;
      background: white;
      border-radius: 50%;
      transition: transform 0.2s ease;
    }

    .setting-toggle.enabled .toggle-switch {
      transform: translateX(24px);
    }

    .settings-actions {
      display: flex;
      gap: 1rem;
      justify-content: flex-end;
      margin-top: 2rem;
      padding-top: 1rem;
      border-top: 1px solid #0f3460;
    }

    .action-button {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .save-button {
      background: #3b82f6;
      color: white;
    }

    .save-button:hover {
      background: #2563eb;
    }

    .cancel-button {
      background: transparent;
      color: #94a3b8;
      border: 1px solid #374151;
    }

    .cancel-button:hover {
      background: rgba(148, 163, 184, 0.1);
    }

    .current-status {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid #3b82f6;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 2rem;
    }

    .status-title {
      color: #60a5fa;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }

    .status-text {
      color: #e2e8f0;
      font-size: 0.875rem;
    }
  `;

    async connectedCallback() {
        super.connectedCallback();
        await this.loadCurrentSettings();
    }

    async loadCurrentSettings() {
        try {
            const response = await fetch('/api/coordinator/settings');
            if (response.ok) {
                const currentSettings = await response.json();
                this.settings = {
                    coordinatorType: currentSettings.coordinator_type,
                    autoSwitchThreshold: currentSettings.auto_switch_threshold,
                    responseTimeoutMs: currentSettings.response_timeout_ms,
                    enableMemoryLearning: currentSettings.enable_memory_learning,
                    debugMode: currentSettings.debug_mode
                };
                this.requestUpdate();
            }
        } catch (error) {
            console.warn('Could not load current settings, using defaults:', error);
        }
    }

    toggleVisibility() {
        this.isVisible = !this.isVisible;
        this.requestUpdate();
    }

    close() {
        this.isVisible = false;
        this.requestUpdate();
    }

    selectCoordinatorType(type: 'fast' | 'memory-enhanced' | 'auto') {
        this.settings = { ...this.settings, coordinatorType: type };
        this.requestUpdate();
    }

    toggleSetting(setting: keyof CoordinatorSettings) {
        if (typeof this.settings[setting] === 'boolean') {
            this.settings = {
                ...this.settings,
                [setting]: !this.settings[setting]
            };
            this.requestUpdate();
        }
    }

    updateNumericSetting(setting: keyof CoordinatorSettings, value: string) {
        const numValue = parseInt(value);
        if (!isNaN(numValue)) {
            this.settings = { ...this.settings, [setting]: numValue };
            this.requestUpdate();
        }
    }

    async saveSettings() {
        try {
            // Save settings to backend API
            const response = await fetch('/api/coordinator/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    coordinator_type: this.settings.coordinatorType,
                    auto_switch_threshold: this.settings.autoSwitchThreshold,
                    response_timeout_ms: this.settings.responseTimeoutMs,
                    enable_memory_learning: this.settings.enableMemoryLearning,
                    debug_mode: this.settings.debugMode
                })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('💾 Settings saved successfully:', result);

                // Dispatch custom event for parent components
                this.dispatchEvent(new CustomEvent('settings-saved', {
                    detail: { ...this.settings, result },
                    bubbles: true
                }));

                this.close();
            } else {
                const error = await response.json();
                console.error('❌ Failed to save settings:', error);
                alert(`Failed to save settings: ${error.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('❌ Error saving settings:', error);
            alert(`Error saving settings: ${error}`);
        }
    }

    render() {
        return html`
      <div class="settings-overlay ${this.isVisible ? 'visible' : ''}">
        <div class="settings-panel">
          <div class="settings-header">
            <h2 class="settings-title">⚙️ Coordinator Settings</h2>
            <button class="close-button" @click=${this.close}>✕</button>
          </div>

          <div class="current-status">
            <div class="status-title">Current Configuration</div>
            <div class="status-text">
              Using <strong>${this.settings.coordinatorType === 'memory-enhanced' ? 'Memory-Enhanced' :
                this.settings.coordinatorType === 'fast' ? 'Fast Rule-Based' : 'Auto-Switching'}</strong> coordinator
              ${this.settings.coordinatorType === 'memory-enhanced' ? '(Natural LLM-based conversation)' :
                this.settings.coordinatorType === 'fast' ? '(Template-based responses)' : '(Intelligent switching)'}
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">Coordinator Type</label>
            <div class="setting-description">
              Choose how the AI coordinator should respond to your requests
            </div>

            <div class="coordinator-type-selector">
              <div class="coordinator-option ${this.settings.coordinatorType === 'fast' ? 'selected' : ''}"
                   @click=${() => this.selectCoordinatorType('fast')}>
                <div class="option-title">⚡ Fast</div>
                <div class="option-subtitle">Rule-based templates</div>
                <div class="option-performance">< 2s response</div>
              </div>

              <div class="coordinator-option ${this.settings.coordinatorType === 'memory-enhanced' ? 'selected' : ''}"
                   @click=${() => this.selectCoordinatorType('memory-enhanced')}>
                <div class="option-title">🧠 Natural</div>
                <div class="option-subtitle">LLM-based conversation</div>
                <div class="option-performance">3-5s response</div>
              </div>

              <div class="coordinator-option ${this.settings.coordinatorType === 'auto' ? 'selected' : ''}"
                   @click=${() => this.selectCoordinatorType('auto')}>
                <div class="option-title">🤖 Auto</div>
                <div class="option-subtitle">Context-dependent</div>
                <div class="option-performance">Adaptive</div>
              </div>
            </div>
          </div>

          <div class="setting-group">
            <label class="setting-label">Advanced Settings</label>

            <div class="setting-control">
              <label style="flex: 1;">Auto-switch threshold (ms)</label>
              <input class="setting-input"
                     type="number"
                     value=${this.settings.autoSwitchThreshold}
                     @input=${(e: any) => this.updateNumericSetting('autoSwitchThreshold', e.target.value)}
                     style="flex: 0 0 120px;">
            </div>

            <div class="setting-control">
              <label style="flex: 1;">Response timeout (ms)</label>
              <input class="setting-input"
                     type="number"
                     value=${this.settings.responseTimeoutMs}
                     @input=${(e: any) => this.updateNumericSetting('responseTimeoutMs', e.target.value)}
                     style="flex: 0 0 120px;">
            </div>

            <div class="setting-control">
              <label style="flex: 1;">Enable memory learning</label>
              <div class="setting-toggle ${this.settings.enableMemoryLearning ? 'enabled' : ''}"
                   @click=${() => this.toggleSetting('enableMemoryLearning')}>
                <div class="toggle-switch"></div>
              </div>
            </div>

            <div class="setting-control">
              <label style="flex: 1;">Debug mode</label>
              <div class="setting-toggle ${this.settings.debugMode ? 'enabled' : ''}"
                   @click=${() => this.toggleSetting('debugMode')}>
                <div class="toggle-switch"></div>
              </div>
            </div>
          </div>

          <div class="settings-actions">
            <button class="action-button cancel-button" @click=${this.close}>
              Cancel
            </button>
            <button class="action-button save-button" @click=${this.saveSettings}>
              💾 Save Settings
            </button>
          </div>
        </div>
      </div>
    `;
    }
}

customElements.define('settings-panel', SettingsPanel);
