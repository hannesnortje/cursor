# Coordinator Settings Feature

## Overview

This feature provides a web-based settings interface for configuring the AI Coordinator behavior in the dashboard. Users can switch between different coordinator modes and adjust advanced parameters.

## Components Created

### 🎨 Frontend Components

#### `settings-panel.ts`
- **Location**: `src/dashboard/frontend/components/settings-panel.ts`
- **Purpose**: Modal settings panel with coordinator configuration options
- **Features**:
  - Coordinator type selection (Fast/Natural/Auto)
  - Advanced settings (timeouts, thresholds)
  - Toggle switches for memory learning and debug mode
  - Real-time API integration
  - Responsive design with modern UI

#### Updated `dashboard-app.ts`
- **Changes**: Integrated settings panel with event handling
- **Features**:
  - Settings panel visibility management
  - Event routing between header and settings
  - State management for settings data

#### Updated `dashboard-header.ts`
- **Changes**: Connected existing settings button to open settings panel
- **Features**: Event dispatching for settings panel activation

### ⚙️ Backend API

#### `coordinator.py`
- **Location**: `src/dashboard/backend/api/coordinator.py`
- **Purpose**: REST API endpoints for coordinator settings management
- **Endpoints**:
  - `GET /api/coordinator/settings` - Get current settings
  - `POST /api/coordinator/settings` - Update settings
  - `GET /api/coordinator/status` - Get coordinator status
  - `POST /api/coordinator/apply-settings` - Apply settings to running system

#### Updated `main.py`
- **Changes**: Registered coordinator API router
- **Route**: `/api/coordinator/*` endpoints now available

## Settings Options

### Coordinator Types

1. **⚡ Fast Mode**
   - Rule-based template responses
   - < 2 second response time
   - Lower resource usage
   - Good for quick interactions

2. **🧠 Natural Mode** (Current Default)
   - LLM-based conversation
   - 3-5 second response time
   - Memory-driven insights
   - Best for detailed planning

3. **🤖 Auto Mode** (Future Enhancement)
   - Context-dependent switching
   - Adaptive response timing
   - Intelligent mode selection

### Advanced Settings

- **Auto-switch threshold**: Response time limit before switching to fast mode
- **Response timeout**: Maximum time to wait for coordinator response
- **Memory learning**: Enable/disable persistent memory storage
- **Debug mode**: Enable detailed logging and debugging information

## Integration Status

### ✅ Completed
- Frontend settings panel UI
- Backend API endpoints
- Settings persistence (in-memory)
- API integration and error handling
- Event-driven architecture

### 🚧 TODO (Future Enhancements)
- **Settings Application**: Connect API to actual coordinator switching in `protocol_server.py`
- **Database Storage**: Replace in-memory settings with persistent database storage
- **Auto Mode**: Implement intelligent coordinator switching based on context
- **Validation**: Add more comprehensive settings validation
- **Hot Reload**: Apply settings without system restart
- **User Preferences**: Per-user settings storage
- **Settings Export/Import**: Backup and restore functionality

## Usage

1. **Access Settings**: Click the ⚙️ Settings button in the dashboard header
2. **Configure Coordinator**: Select desired coordinator type and adjust parameters
3. **Save Changes**: Click "💾 Save Settings" to apply configuration
4. **View Status**: Current configuration shown in blue status box

## API Examples

### Get Current Settings
```bash
curl http://localhost:8000/api/coordinator/settings
```

### Update Settings
```bash
curl -X POST http://localhost:8000/api/coordinator/settings \
  -H "Content-Type: application/json" \
  -d '{
    "coordinator_type": "memory-enhanced",
    "auto_switch_threshold": 5000,
    "response_timeout_ms": 10000,
    "enable_memory_learning": true,
    "debug_mode": false
  }'
```

## Architecture Notes

- **Frontend**: Lit 3.0 web components with TypeScript
- **Backend**: FastAPI with Pydantic models
- **State Management**: Event-driven with custom events
- **Styling**: CSS with modern gradients and animations
- **Error Handling**: Comprehensive try-catch with user feedback

## Why This Was Created

This feature was created as a "minimal version" to ensure we don't forget to implement coordinator configuration options. It provides:

1. **Future-Proofing**: Infrastructure ready for when we need coordinator switching
2. **User Control**: Allows users to choose between fast vs natural coordination
3. **Development Aid**: Settings interface for testing different coordinator behaviors
4. **Scalability**: Foundation for more advanced configuration options

The implementation is production-ready but has placeholder TODOs for actual coordinator switching integration.
