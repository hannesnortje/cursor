// Type declarations for Lit 3
declare module 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js' {
  export class LitElement extends HTMLElement {
    static properties?: Record<string, any>;
    static styles?: any;
    
    render(): any;
    connectedCallback(): void;
    disconnectedCallback(): void;
    requestUpdate(name?: string, oldValue?: any): void;
    update(changedProperties: Map<string, any>): void;
    firstUpdated(changedProperties: Map<string, any>): void;
    updated(changedProperties: Map<string, any>): void;
    
    readonly shadowRoot: ShadowRoot;
    dispatchEvent(event: Event): boolean;
  }
  
  export const html: (strings: TemplateStringsArray, ...values: any[]) => any;
  export const css: (strings: TemplateStringsArray, ...values: any[]) => any;
}

// Global type declarations for custom elements
declare global {
  interface HTMLElementTagNameMap {
    'dashboard-app': DashboardApp;
    'dashboard-header': DashboardHeader;
    'system-health-card': SystemHealthCard;
    'agents-status-card': AgentsStatusCard;
    'performance-card': PerformanceCard;
    'quick-actions-card': QuickActionsCard;
    'dashboard-footer': DashboardFooter;
  }
}

// Base component class interface
interface BaseComponent extends HTMLElement {
  shadowRoot: ShadowRoot;
  dispatchEvent(event: Event): boolean;
  connectedCallback?(): void;
  disconnectedCallback?(): void;
}

// Component class interfaces
interface DashboardApp extends BaseComponent {}
interface DashboardHeader extends BaseComponent {}
interface SystemHealthCard extends BaseComponent {}
interface AgentsStatusCard extends BaseComponent {}
interface PerformanceCard extends BaseComponent {}
interface QuickActionsCard extends BaseComponent {}
interface DashboardFooter extends BaseComponent {}
