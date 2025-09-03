# 🚀 **Quick Reference: Essential Test Prompts**

## **🔥 Start Here (Basic Tests)**

```
/system_health
/start_project test basic "Quick Test Project"
/get_communication_status
```

## **🎯 Core Features (Must Test)**

```
/chat_with_coordinator {"type": "project_generation", "action": "list_templates"}
/create_agile_project "Test Project" "scrum" 14 5
/list_project_templates
/broadcast_message "test" "agent" "Hello!" ["chat1"]
```

## **💾 New Qdrant Integration (Phase 2.5)**

```
/start_project "vector_test" "Vector Test Project"
/broadcast_message "vector_chat" "vector_agent" "Testing vector storage" ["chat1"]
/get_cross_chat_messages
/search_cross_chat_messages "vector"
```

## **📊 Status & Monitoring**

```
/system_overview
/project_status
/storage_status
```

---

## **📱 How to Use**

1. **Copy** any prompt above
2. **Paste** in Cursor chat
3. **Send** and observe response
4. **Test** different combinations

## **🎯 Testing Order**

1. **System Health** → Basic functionality
2. **Vector Storage** → New Qdrant integration  
3. **Coordinator** → Core agent system
4. **Agile Features** → Specialized agents
5. **Cross-Chat** → Communication system
6. **Project Gen** → Template system

---

**Start with `/system_health` and work your way up! 🚀**
