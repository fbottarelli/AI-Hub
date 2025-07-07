# 🌐 Agno Multi-Source RAG System

An intelligent multi-source chatbot that identifies projects from questions and retrieves information from multiple data sources in parallel, then combines the information for comprehensive answers.

## 🎯 **System Overview**

This system reimplements the sophisticated multi-source RAG system from `sources_langgraph` using the modern Agno framework. It demonstrates how to migrate from LangGraph's node-based workflow orchestration to Agno's intelligent agent-based architecture.

## 🔍 **Core Intelligence**

### **Project-Aware Context Recognition**
- **Identifies projects** from user questions using multiple methods
- **Maintains context** across conversation turns
- **Validates project names** through centralized project management
- **Handles multi-project queries** and general information requests

### **Parallel Multi-Source Retrieval**
The system retrieves information from **5 parallel sources**:

1. **📋 Verbali** - Meeting minutes, RFC evaluations, technical discussions
2. **📄 User Documents** - Personal uploads, project-specific documents  
3. **🗄️ Athena SQL** - Structured project metadata, catalogs, KPIs
4. **📖 MI Documentation** - Installation manuals, technical procedures
5. **📚 Wiki Knowledge Base** - Organizational processes, standards

### **Intelligent Information Synthesis**
- **Combines all sources** into coherent responses
- **Prioritizes relevant information** based on query type
- **Maintains conversation context** for follow-up questions
- **Handles source failures** gracefully with partial results

## 🏗️ **Architecture**

```
User Question → Project Identification → Parallel Retrieval → Information Synthesis → Response
                        ↓                       ↓
            [Project Context Manager]   [5 Retrieval Agents]
                                              ↓
                        [Verbali] [User Docs] [Athena] [MI] [Wiki]
```

## 🛠️ **Technical Innovation**

### **Original LangGraph Challenges:**
- ~3000 lines of complex state management
- Manual orchestration of retrieval nodes
- Complex conditional logic for source selection
- Difficult error handling and recovery

### **Agno Solution Benefits:**
- **AI-Powered Orchestration**: Agent decides which sources to query
- **Parallel Tool Execution**: Automatic concurrent retrieval
- **Built-in Error Recovery**: Graceful handling of source failures  
- **Simplified State Management**: Agent handles context automatically
- **Easy Extensibility**: Add new sources as simple tools

## 📊 **Use Cases**

### **Multi-Project Intelligence**
- *"Compare the change managers for SIRCA and ANAG projects"*
- *"What services are used in the BICREV project?"*
- *"Show me recent decisions about the SIRCA database migration"*

### **Cross-Source Information**
- *"What's the status of Project Alpha and who attended the last meeting?"*
- *"Find installation procedures for ANAG in the MI docs"*
- *"What does our wiki say about the approval process for changes?"*

### **Context-Aware Conversations**
```
Turn 1: "Tell me about SIRCA" → Identifies SIRCA project
Turn 2: "Who is the change manager?" → Continues SIRCA context
Turn 3: "What about ANAG instead?" → Switches to ANAG project
```

## 🔧 **Project Structure**

```
agno_multi_source/
├── src/agno_multi_source/
│   ├── models.py              # Data models for multi-source system
│   ├── config.py              # Configuration management
│   ├── agent.py               # Main multi-source agent
│   ├── tools/
│   │   ├── project_tools.py   # Project identification & validation
│   │   ├── verbali_tools.py   # Meeting minutes retrieval
│   │   ├── athena_tools.py    # SQL catalog queries
│   │   ├── mi_tools.py        # Installation manual tools
│   │   ├── wiki_tools.py      # Wiki knowledge retrieval
│   │   ├── user_docs_tools.py # User document retrieval
│   │   └── synthesis_tools.py # Information combination
│   └── libs/
│       ├── project_manager.py # Centralized project management
│       ├── aws_clients.py     # AWS service connections
│       └── qdrant_clients.py  # Vector database connections
├── docs/
│   ├── architecture.md       # System architecture
│   └── migration-guide.md    # LangGraph to Agno migration
├── tests/                    # Test suite
└── requirements.txt          # Dependencies
```

## 🚀 **Getting Started**

```bash
cd experiments/agno_multi_source
uv sync
cp .env.example .env  # Configure your credentials
uv run python src/agno_multi_source/agent.py
```

## 🎯 **Development Status**

- [x] Project structure created
- [x] Architecture designed  
- [ ] Project identification tools
- [ ] Parallel retrieval tools implementation
- [ ] Information synthesis tools
- [ ] Main agent implementation
- [ ] Testing framework
- [ ] Integration with existing data sources

## 📈 **Migration Benefits**

Moving from LangGraph to Agno provides:
- **90% less code** for the same functionality
- **Built-in parallelization** of retrieval operations
- **Automatic error recovery** and retry logic
- **Simplified maintenance** and extensibility
- **Better observability** and debugging capabilities

---

*This project demonstrates the power of modern agent frameworks in simplifying complex multi-source RAG systems while maintaining sophisticated functionality.* 