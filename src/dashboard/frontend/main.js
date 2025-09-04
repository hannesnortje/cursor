// Main entry point for the dashboard
// Import all components in dependency order

// Import child components first
import './dist/components/dashboard-header.js';
import './dist/components/system-health-card.js';
import './dist/components/agents-status-card.js';
import './dist/components/performance-card.js';
import './dist/components/quick-actions-card.js';
import './dist/components/dashboard-footer.js';

// Import the main dashboard app component last (depends on child components)
import './dist/components/dashboard-app.js';

console.log('🚀 Dashboard components loaded successfully!');
console.log('📱 All components are now available as custom elements:');

// Check if components are properly registered
setTimeout(() => {
    console.log('🔍 Checking component registration:');
    console.log('  - <dashboard-app>:', customElements.get('dashboard-app') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <dashboard-header>:', customElements.get('dashboard-header') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <system-health-card>:', customElements.get('system-health-card') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <agents-status-card>:', customElements.get('agents-status-card') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <performance-card>:', customElements.get('performance-card') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <quick-actions-card>:', customElements.get('quick-actions-card') ? '✅ Registered' : '❌ Not registered');
    console.log('  - <dashboard-footer>:', customElements.get('dashboard-footer') ? '✅ Registered' : '❌ Not registered');
    
    // Check if dashboard-app element exists in DOM
    const dashboardApp = document.querySelector('dashboard-app');
    console.log('🔍 Dashboard app element in DOM:', dashboardApp ? '✅ Found' : '❌ Not found');
    
    if (dashboardApp) {
        console.log('🔍 Dashboard app shadow root:', dashboardApp.shadowRoot ? '✅ Has shadow root' : '❌ No shadow root');
    }
}, 100);
