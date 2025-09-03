# 🧪 Cursor Chat Test Prompts

This file contains all the prompts you can use to test the AI Agent System through Cursor chats. Copy and paste these prompts into your Cursor chat to test different functionalities.

---

## 🚀 **Phase 1: Basic System & MCP Server**

### **System Health Check**
```
/system_health
```

### **Start a Basic Project**
```
/start_project test basic "My First Test Project"
```

---

## 🎯 **Phase 2: AutoGen Integration & Vector Database**

### **Test LLM Gateway**
```
/test_llm_gateway
```

### **Test AutoGen Integration**
```
/test_autogen_integration
```

### **Test Vector Database**
```
/test_vector_store
```

### **Test Enhanced Communication**
```
/test_enhanced_communication
```

---

## 🎭 **Phase 3: Coordinator Agent & PDCA Framework**

### **Chat with Coordinator**
```
/chat_with_coordinator {"type": "project_generation", "action": "list_templates"}
```

### **Start Project with PDCA**
```
/start_project agile "PDCA Test Project"
```

### **Get Project Status**
```
/get_project_status
```

---

## 🌐 **Phase 4: Communication System & Cross-Chat**

### **Test Cross-Chat Communication**
```
/broadcast_message "test_chat" "test_agent" "Hello from test chat!" ["chat1", "chat2"]
```

### **Get Cross-Chat Messages**
```
/get_cross_chat_messages
```

### **Search Cross-Chat Messages**
```
/search_cross_chat_messages "test"
```

### **Get Communication Status**
```
/get_communication_status
```

---

## 📋 **Phase 5.1: Agile/Scrum Agent**

### **Create Agile Project**
```
/create_agile_project "Sprint Planning Project" "scrum" 14 6
```

### **Create User Story**
```
/create_user_story "project_id_here" "User Authentication" "Implement secure user login system" ["User can log in", "User can reset password"] 8 "high" "Security Epic"
```

### **Create Sprint**
```
/create_sprint "project_id_here" "Sprint 1" "2025-09-01" "2025-09-14" "Complete user authentication features"
```

### **Get Project Status**
```
/get_project_status "project_id_here"
```

### **Get Sprint Burndown**
```
/get_sprint_burndown "sprint_id_here"
```

### **Calculate Team Velocity**
```
/calculate_team_velocity "project_id_here" 3
```

---

## 🏗️ **Phase 5.2: Project Generation Agent**

### **List Project Templates**
```
/list_project_templates
```

### **List Templates by Language**
```
/list_project_templates python
```

### **List Templates by Category**
```
/list_project_templates "web"
```

### **Generate Project from Template**
```
/generate_project "template_id_here" "My New Project" "/path/to/target"
```

### **Create Custom Project**
```
/create_custom_project "My Custom Project" "typescript" {"structure": "custom"}
```

---

## 🔗 **Phase 2.5: Qdrant Integration (New!)**

### **Test Vector Store Integration**
```
/test_qdrant_integration
```

### **Test Project Context Storage**
```
/start_project "vector_test" "Vector Database Test Project"
```

### **Test Message Vector Storage**
```
/broadcast_message "vector_chat" "vector_agent" "Testing vector storage capabilities" ["chat1"]
```

### **Get Vector Store Status**
```
/get_communication_status
```

---

## 🧪 **Comprehensive Testing Prompts**

### **Full System Test**
```
/test_full_system
```

### **Test All Agents**
```
/test_all_agents
```

### **Test All Communication Methods**
```
/test_all_communication
```

### **Test All Storage Methods**
```
/test_all_storage
```

---

## 📊 **Status & Monitoring Prompts**

### **Get System Overview**
```
/system_overview
```

### **Get Agent Status**
```
/agent_status
```

### **Get Project Status**
```
/project_status
```

### **Get Storage Status**
```
/storage_status
```

---

## 🔧 **Debug & Troubleshooting Prompts**

### **Check System Logs**
```
/check_logs
```

### **Test Error Handling**
```
/test_error_handling
```

### **Check Dependencies**
```
/check_dependencies
```

### **Test Fallback Systems**
```
/test_fallbacks
```

---

## 📝 **Usage Instructions**

1. **Copy** any prompt from above
2. **Paste** it into your Cursor chat
3. **Send** the message
4. **Observe** the response and system behavior
5. **Test** different combinations and scenarios

---

## 🎯 **Testing Strategy**

### **Start Simple**
- Begin with basic system health checks
- Test one feature at a time
- Verify expected responses

### **Test Integration**
- Test features that depend on each other
- Verify data flows between components
- Check fallback mechanisms

### **Test Edge Cases**
- Test with invalid inputs
- Test when services are unavailable
- Test error handling

### **Performance Testing**
- Test with multiple concurrent requests
- Monitor response times
- Check resource usage

---

## 🚨 **Important Notes**

- **Qdrant Server**: Some features require a running Qdrant server
- **Redis Server**: Cross-chat features require Redis
- **Fallbacks**: System gracefully falls back to in-memory storage
- **Async Operations**: Some operations run in background threads
- **Error Handling**: System logs errors and continues operation

---

## 🔄 **Test Sequence Recommendation**

1. **System Health** → Verify basic functionality
2. **Basic Project** → Test core project management
3. **Vector Storage** → Test new Qdrant integration
4. **Cross-Chat** → Test communication system
5. **Agile Features** → Test specialized agents
6. **Project Generation** → Test template system
7. **Integration** → Test component interactions
8. **Error Scenarios** → Test robustness

---

**Happy Testing! 🎉**
