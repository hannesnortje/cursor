# 🧪 AI Agent System - Test Suite

This directory contains the comprehensive test suite for the AI Agent System.

## 📁 **Test Organization**

### **End-to-End Tests** (`end_to_end/`)
- **`test_system_ready.py`** - System readiness verification

### **Integration Tests** (`integration/`)
- **`test_phase2_autogen_qdrant_llm.py`** - AutoGen + Qdrant + LLM Gateway
- **`test_phase5_1_agile_agent.py`** - Agile/Scrum Agent functionality
- **`test_phase5_2_project_generation.py`** - Project Generation Agent
- **`test_qdrant_integration.py`** - Qdrant integration with main system

### **Unit Tests** (`unit/`)
- **`test_phase3_coordinator.py`** - Coordinator Agent functionality
- **`test_enhanced_server.py`** - Enhanced MCP server features

## 🚀 **Running Tests**

### **Run All Tests**
```bash
python3 tests/run_all_tests.py
```

### **Run Specific Test Categories**
```bash
# End-to-end tests
python3 tests/end_to_end/test_system_ready.py

# Integration tests
python3 tests/integration/test_phase2_autogen_qdrant_llm.py

# Unit tests
python3 tests/unit/test_phase3_coordinator.py
```

### **Run Individual Tests**
```bash
# Test specific functionality
python3 tests/integration/test_qdrant_integration.py
```

## 📊 **Test Categories**

### **End-to-End Tests**
- Verify complete system functionality
- Test system readiness
- Validate overall integration

### **Integration Tests**
- Test component interactions
- Verify data flow between systems
- Test fallback mechanisms

### **Unit Tests**
- Test individual components
- Validate specific functionality
- Test error handling

## 🎯 **Test Coverage**

- ✅ **Phase 1**: Project Foundation & MCP Server
- ✅ **Phase 2**: AutoGen Integration & Vector Database
- ✅ **Phase 3**: Coordinator Agent & PDCA Framework
- ✅ **Phase 4**: Communication System & Cross-Chat
- ✅ **Phase 5.1**: Agile/Scrum Agent
- ✅ **Phase 5.2**: Project Generation Agent
- ✅ **Phase 2.5**: Qdrant Integration with Main System

## 🔧 **Test Requirements**

### **Dependencies**
- Python 3.10+
- Poetry environment activated
- All required packages installed

### **External Services** (Optional)
- Qdrant server (for vector storage tests)
- Redis server (for cross-chat tests)
- LLM services (for AutoGen tests)

### **Fallback Behavior**
- Tests gracefully handle missing services
- System continues functioning with fallbacks
- All core functionality remains available

## 📝 **Adding New Tests**

### **Test File Structure**
```python
#!/usr/bin/env python3
"""Test description for the AI Agent System."""

def test_feature_name():
    """Test specific feature functionality."""
    # Test implementation
    pass

if __name__ == "__main__":
    # Run test
    test_feature_name()
```

### **Test Naming Convention**
- **Unit tests**: `test_component_name.py`
- **Integration tests**: `test_feature_integration.py`
- **End-to-end tests**: `test_system_feature.py`

## 🚨 **Troubleshooting**

### **Common Issues**
- **Import errors**: Ensure Poetry environment is activated
- **Service errors**: Check if external services are running
- **Timeout errors**: Increase timeout in test runner

### **Debug Mode**
```bash
# Run with verbose output
python3 -v tests/run_all_tests.py
```

## 📈 **Test Results**

Tests provide comprehensive coverage of:
- **System functionality** - Core features and capabilities
- **Integration points** - Component interactions
- **Error handling** - Graceful degradation
- **Performance** - Response times and resource usage
- **Fallback systems** - Service availability handling

---

**Happy Testing! 🎉**
