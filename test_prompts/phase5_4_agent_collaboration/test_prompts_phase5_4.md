# Phase 5.4: Agent Collaboration Testing Prompts

## 🎯 **Testing Goal: Verify All Specialized Agents Work Together**

**Test Directory:** `/media/hannesn/storage/Code/Test/phase5_4_agent_collaboration/`

**Objective:** Test how the Coordinator Agent orchestrates all specialized agents (Agile, Project Generation, Backend) to work together seamlessly.

---

## 🚀 **Phase 5.4 Test Prompts for Cursor Chat**

### **1. 🧪 Basic System Health & Agent Status**

```
Check the system health and show me all available agents
```

**Expected Response:** System health report showing all agents (Coordinator, Agile, Project Generation, Backend) with their status.

---

### **2. 🔄 Coordinator Agent Communication Test**

```
Hello Coordinator! Can you tell me what agents you can work with and what they can do?
```

**Expected Response:** Coordinator should list all available specialized agents and their capabilities.

---

### **3. 🏗️ Multi-Agent Project Creation Workflow**

```
Coordinator, I want to create a new web application project. Can you help me:
1. Start a new project with the PDCA framework
2. Set up an agile workflow for it
3. Generate the initial project structure
4. Design a basic REST API for it
```

**Expected Response:** Coordinator should orchestrate:
- Agile Agent: Create project with PDCA framework
- Project Generation Agent: Generate project structure
- Backend Agent: Design REST API specification

---

### **4. 📊 Agile + Project Generation Collaboration**

```
Coordinator, I need to:
1. Create a new agile project called "E-commerce Platform"
2. Generate a Python FastAPI project structure for it
3. Create some user stories for the first sprint
```

**Expected Response:** Coordinator should coordinate:
- Agile Agent: Create agile project and user stories
- Project Generation Agent: Generate Python FastAPI structure

---

### **5. 🔧 Backend + Project Generation Integration**

```
Coordinator, please help me:
1. Design a REST API for user management
2. Generate the Python FastAPI code for it
3. Create a database schema for users
4. Set up JWT authentication
```

**Expected Response:** Coordinator should orchestrate:
- Backend Agent: Design API, create database schema, implement security
- Project Generation Agent: Generate the actual code files

---

### **6. 🎯 Complex Multi-Agent Workflow**

```
Coordinator, I want to build a complete microservices architecture:
1. Start a new agile project called "Microservices Platform"
2. Design the overall architecture (microservices pattern)
3. Generate separate projects for each service
4. Design APIs for each service
5. Set up security across all services
6. Create the first sprint with user stories
```

**Expected Response:** This should trigger a complex orchestration involving all agents working together.

---

### **7. 🔍 Agent Capability Discovery**

```
Coordinator, can you show me what each of your specialized agents can do? I want to understand their full capabilities.
```

**Expected Response:** Detailed breakdown of each agent's capabilities and how they can work together.

---

### **8. 🧪 Cross-Agent Data Sharing**

```
Coordinator, I created an API specification with the Backend Agent. Can you now use the Project Generation Agent to create the actual project files based on that specification?
```

**Expected Response:** Coordinator should retrieve the API specification from Backend Agent and use it to generate project files.

---

### **9. 📈 Agile + Backend Integration**

```
Coordinator, I'm working on a sprint and need to:
1. Create user stories for API development
2. Design the API endpoints
3. Generate the code for those endpoints
4. Track the progress in the sprint
```

**Expected Response:** Coordinator should coordinate Agile Agent for sprint management and Backend Agent for API development.

---

### **10. 🎨 End-to-End Workflow Test**

```
Coordinator, let's do a complete project from start to finish:
1. Start a new agile project called "Full-Stack Dashboard"
2. Plan the first sprint with user stories
3. Design the backend API architecture
4. Generate the project structure
5. Create the database schemas
6. Implement authentication
7. Generate all the code
8. Show me the sprint progress
```

**Expected Response:** This should demonstrate the complete orchestration capabilities of all agents working together.

---

## 🔍 **What to Look For:**

### **✅ Success Indicators:**
- **Coordinator Agent** successfully delegates tasks to specialized agents
- **Agile Agent** creates projects, sprints, and user stories
- **Project Generation Agent** generates project structures and code
- **Backend Agent** designs APIs, databases, and security
- **Cross-agent communication** works seamlessly
- **Data persistence** between agent interactions
- **Error handling** when agents encounter issues

### **⚠️ Potential Issues to Watch:**
- Agents not communicating properly
- Data not being shared between agents
- Coordinator failing to orchestrate multiple agents
- MCP tools not working for agent coordination
- Import errors or missing dependencies

---

## 🚀 **Testing Sequence:**

1. **Start with basic prompts** (1-2) to verify system health
2. **Test simple collaborations** (3-4) to verify basic agent interaction
3. **Test complex workflows** (5-6) to verify advanced orchestration
4. **Test end-to-end scenarios** (7-10) to verify complete system integration

---

## 📝 **Test Results Template:**

For each test prompt, note:
- **Response received:** What the system actually returned
- **Expected vs actual:** Did it match expectations?
- **Agent coordination:** Did multiple agents work together?
- **Data flow:** Was information shared between agents?
- **Issues encountered:** Any errors or unexpected behavior?

---

## 🎯 **Success Criteria for Phase 5.4:**

- ✅ **All agents respond** to Coordinator requests
- ✅ **Cross-agent workflows** execute successfully
- ✅ **Data persistence** works between agent interactions
- ✅ **Complex orchestration** handles multi-step processes
- ✅ **Error handling** gracefully manages failures
- ✅ **MCP tools** work for all agent coordination tasks

---

**Ready to test? Start with the basic prompts and work your way up to the complex workflows! 🚀**
