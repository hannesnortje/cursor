// Main entry point for the dashboard
// Import all components in dependency order

// Import child components first
import '/static/dist/components/dashboard-header.js';
import '/static/dist/components/system-health-card.js';
import '/static/dist/components/agents-status-card.js';
import '/static/dist/components/performance-card.js';
import '/static/dist/components/quick-actions-card.js';
import '/static/dist/components/dashboard-footer.js';

// Import the main dashboard app component last (depends on child components)
import '/static/dist/components/dashboard-app.js';

console.log('🚀 Dashboard components loaded successfully!');
console.log('📱 All components are now available as custom elements:');

// Dashboard will be automatically closed by MCP server when Cursor disconnects
console.log('📱 Dashboard ready - will auto-close when Cursor disconnects');

// Monitor for dashboard shutdown and close browser tab
let shutdownDetected = false;

function checkDashboardStatus() {
    if (shutdownDetected) return;
    
    fetch('/api/health')
        .then(response => {
            if (!response.ok) {
                console.log('🔄 Dashboard health check failed, attempting to close tab...');
                shutdownDetected = true;
                closeTab();
            }
        })
        .catch(error => {
            console.log('🔄 Dashboard unreachable, attempting to close tab...');
            shutdownDetected = true;
            closeTab();
        });
}

function closeTab() {
    // Try multiple methods to close the tab
    console.log('🔄 Attempting to close browser tab...');
    
    // Method 1: Standard window.close()
    try {
        window.close();
        console.log('✅ window.close() called');
    } catch (e) {
        console.log('⚠️ window.close() failed:', e);
    }
    
    // Method 2: Try to navigate away (works in some cases)
    setTimeout(() => {
        try {
            window.location.href = 'about:blank';
            console.log('✅ Navigated to about:blank');
        } catch (e) {
            console.log('⚠️ Navigation failed:', e);
        }
    }, 1000);
    
    // Method 3: Show a message to user
    setTimeout(() => {
        document.body.innerHTML = `
            <div style="
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                justify-content: center; 
                height: 100vh; 
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            ">
                <h1>🔄 Dashboard Shutdown</h1>
                <p>The MCP server has disconnected and this dashboard is no longer available.</p>
                <p>You can safely close this tab.</p>
                <div style="margin-top: 20px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 8px;">
                    <p><strong>Status:</strong> Disconnected</p>
                    <p><strong>Reason:</strong> Cursor window was closed</p>
                </div>
            </div>
        `;
        console.log('✅ Displayed shutdown message');
    }, 2000);
}

// Check dashboard health every 2 seconds
setInterval(checkDashboardStatus, 2000);

// Also listen for beforeunload to detect when the page is being closed
window.addEventListener('beforeunload', () => {
    console.log('👋 Dashboard tab closing...');
});

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
