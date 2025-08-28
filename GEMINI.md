## Project Overview

The Multi-Agent Project Management System is an intelligent multi-agent framework designed to automate the creation and management of software project documentation. The agents collaborate to:

-   **Automate the creation** of technical and organizational documentation.
-   **Manage change management** with automatic updates.
-   **Gather requirements** through intelligent interaction.
-   **Generate project plans** based on best practices.
-   **Maintain consistency** between documentation and code.

The target audience includes users seeking assistance with project planning and adherence to Project Management Institute (PMI) standards.

## Architecture & Structure

### High-level Architecture Overview

The system employs a multi-agent architecture built on the AutoGen framework, utilizing an event-driven pattern with asynchronous message passing between specialized agents.

```
┌─────────────────────────────────────────────────────┐
│                 Knowledge Base                      │
│                 (JSON-LD)                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│   │Methodologies│  │  Templates  │  │ Best        │ │
│   │(Agile,      │  │(Project     │  │ Practices   │ │
│   │Waterfall)   │  │Charter,PRD) │  │             │ │
│   └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│              Multi-Agent System                     │
│                                                     │
│  ┌─────────────┐    ┌─────────────┐                │
│  │ Project     │◄──►│Requirements │                │
│  │ Manager     │    │ Analyst     │                │
│  └─────────────┘    └─────────────┘                │
│         │                   │                      │
│         ▼                   ▼                      │
│  ┌─────────────┐    ┌─────────────┐                │
│  │ Change      │    │ Technical   │                │
│  │ Detector    │    │ Writer      │                │
│  └─────────────┘    └─────────────┘                │
│                                                     │
│         ▲                                           │
│         │ Ollama API (Local LLM)                   │
│         ▼                                           │
└─────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────┐
│               Document Store                        │
│              (File System)                         │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│   │Project      │  │Requirements │  │Technical    │ │
│   │Charter      │  │Documents    │  │Specs        │ │
│   └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Architectural Patterns

-   **Event-Driven Architecture**: Agents react to events and messages.
-   **Microservices Pattern**: Each agent has specific responsibilities.
-   **Repository Pattern**: Separation between business logic and data persistence.
-   **Strategy Pattern**: Interchangeable methodologies (Agile, Waterfall).

### Technologies Used

#### Core Framework

-   **AutoGen**: Microsoft framework for multi-agent systems.
-   **Ollama and Deepseek**: Two usable Large Language Models.
-   **Python 3.12+**: Main programming language.

#### Data Models

-   **JSON-LD**: Knowledge representation for entities and relationships.
-   **Dataclasses**: Typed Python data structures.
-   **Pydantic**: Data validation and serialization.

#### Persistence

-   **File System**: Storage for generated documents.
-   **JSON**: Indexing and metadata.
-   **Markdown**: Document output format.

#### Communication

-   **HTTP/REST**: Integration with Ollama API.
-   **Message Passing**: Communication between agents.
-   **Async/Await**: Management of asynchronous operations.

### File Structure

```
backend/      # python code root folder
│
├── models/
│   ├── __init__.py
│   └── data_models.py          # Dataclasses and enums
│
├── knowledge/
│   ├── __init__.py
│   ├── knowledge_base.py       # JSON-LD knowledge base management
│   └── knowledge_base.jsonld   # KB with methodologies and templates
│
├── storage/
│   ├── __init__.py
│   └── document_store.py       # Persistence of output documents
│
├── agents/
│   ├── __init__.py            # Export agents and factory function
│   ├── base_agent.py          # Base class for agents
│   ├── project_manager.py     # Orchestrator agent
│   ├── requirements_analyst.py # Requirements gathering agent
│   ├── change_detector.py     # Change management agent
│   └── technical_writer.py    # Technical documentation agent
│
├── output_documents/          # Directory of generated documents
│   ├── document_index.json   # Document index
│   └── [generated_docs].md   # Markdown documents
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_knowledge_base.py
│   └── test_document_store.py
│
├── config/
│   ├── __init__.py
│   └── settings.py           # System configurations
│
├── main.py                   # Demo and main runner
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## Development Setup

### Prerequisites

1.  **Python 3.12+** installed
2.  **Ollama** installed and configured
3.  **Git** for cloning the project
4.  **Node.js and npm** for the frontend

### Step 1: Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download installer from https://ollama.ai/download

# Start the service
ollama serve
```

### Step 2: Download LLM Model

```bash
# Download recommended model (about 2GB)
ollama pull llama3.2

# Verify available models
ollama list

# Test model
ollama run llama3.2 "Hello, how are you?"
```

### Step 3: Configure LLM Provider

The system can use two LLM providers: **DeepSeek** (cloud-based) or **Ollama** (local).

Create a `.env` file in the project root and set the following variables:

```env
# Choose the provider: "deepseek" or "ollama"
LLM_PROVIDER=ollama

# --- Configuration for DeepSeek (if LLM_PROVIDER="deepseek") ---
# DEEPSEEK_API_KEY=your_deepseek_api_key

# --- Configuration for Ollama (if LLM_PROVIDER="ollama") ---
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

**Note:** Make sure you have installed and started Ollama if you select it as a provider.

### Step 4: Setup Backend

```bash
# Clone the project
git clone <repository_url>
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Setup Frontend

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

## How to Run the Project

The project has two main parts: the **backend server** and the **frontend application**.

### Backend Server

The backend is a FastAPI server that provides a WebSocket interface for the agent team.

To run the server, execute the following command from the `backend` directory:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend Application

The frontend is a React-based chat interface.

To run the frontend, navigate to the `frontend` directory and run the following command:

```bash
# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173` by default and will connect to the backend server running on port 8001.

## Agent Implementation

### Implemented Agents

✅ **BaseProjectAgent**: Base class with common functionalities
✅ **ProjectManagerAgent**: Workflow orchestration and project coordination
✅ **RequirementsAnalystAgent**: Requirements gathering, analysis, and validation
✅ **ChangeDetectorAgent**: Change monitoring and management
✅ **TechnicalWriterAgent**: Generation and management of technical documentation

### Implemented Features

-   **OOP Pattern**: Each agent has specific and well-defined responsibilities.
-   **Async/Await**: Asynchronous management for non-blocking operations.
-   **DeepSeek Integration**: Use of LLM for intelligent content generation.
-   **Error Handling**: Robust error handling with logging.
-   **Message Processing**: Message routing system by command type.
-   **Document Management**: Integration with storage and knowledge base.

### Supported Commands

#### Project Manager

-   `init_project` - Initialize a new project
-   `status` - Current project status
-   `requirements` - Start requirements gathering
-   `plan project` - Project planning

#### Requirements Analyst

-   `gather requirements` - Gather requirements from text
-   `analyze requirements` - Analyze gathered requirements
-   `document requirements` - Create formal documentation
-   `interview questions` - Questions for stakeholder interviews
-   `validate requirements` - Validate requirements quality

#### Change Detector

-   `monitor artifacts` - Configure monitoring
-   `detect changes` - Detect changes
-   `analyze impact` - Analyze the impact of changes
-   `change history` - History of changes
-   `approve changes` - Manage approval workflow
-   `rollback changes` - Manage rollback

#### Technical Writer

-   `create document` - Create technical documents
-   `format document` - Apply formatting
-   `review document` - Review documents
-   `template management` - Manage templates
-   `export document` - Export in different formats
-   `organize documents` - Organize documents

## Testing Strategy

### Testing frameworks used

The codebase uses `pytest` for testing, with `conftest.py` providing common fixtures and utilities.

### Test file organization

Test files are located in the `backend/tests/` directory.

### How to run tests

To run tests, `pytest` would typically be invoked from the command line in the project root.

```bash
# Run unit tests
pytest tests/

# Specific test
pytest tests/test_agents.py -v

# Test with coverage
pytest --cov=agents tests/
```

## Future Extensions

-   **ZeroMQ**: Inter-process communication
-   **Web Interface**: Monitoring dashboard
-   **Database Integration**: PostgreSQL for persistence
-   **CI/CD Integration**: Deployment automation
-   **Metrics & Monitoring**: System observability

---
Generated using [Sidekick Dev]({REPO_URL}), your coding agent sidekick.
