## Project Overview
The Multi-Agent Project Management System automates project management tasks using intelligent agent collaboration.  Its main goal is to guide users through PMI best practices and create comprehensive project management plans in markdown format.  The target audience includes users seeking assistance with project planning and adherence to Project Management Institute (PMI) standards. 

## Architecture & Structure
### High-level architecture overview
The system employs a multi-agent architecture built on the AutoGen framework, utilizing an event-driven pattern with asynchronous message passing between specialized agents.  The core components include a `SingleThreadedAgentRuntime`, an `AgentFactory`, and a `ChatCompletionClient` for LLM integration. 

### Key directories and their purposes
*   `backend/agents/`: Contains the implementations of various agents like `TriageAgent`, `ProjectManagementAgent`, and `AgentFactory`. 
*   `backend/config/`: Manages system configurations, including LLM provider settings, logging, and runtime parameters. 
*   `backend/base/`: Provides base classes and utilities, such as the base agent class `AIAgent` and `configure_oltp_tracing` to add observability through OpenTelemetry. 
*   `backend/models/`: Defines data models used across the system, such as `Project` and `UserStory`. 
*   `backend/tests/`: Contains test files and fixtures for the system. 
*   `frontend/`: Contains the React-based frontend application for interacting with the agent system.

### Main components and how they interact
The `main()` function in `backend/main.py` orchestrates the system startup.  It initializes the `ConfigManager`, sets up logging, configures OpenTelemetry tracing, creates a `SingleThreadedAgentRuntime`, and initializes the `ChatCompletionClient`.  The `AgentFactory` then registers all agents and their subscriptions with the runtime.  Agents communicate via a message-based publish-subscribe pattern using `TopicId` instances. 

### Data flow and system design
The system's data flow begins with a `UserLogin` message published to the `USER_TOPIC_TYPE`.  The `TriageAgent` acts as the entry point, routing user requests to specialized agents based on the request's content.  Agents process messages using their `handle_task` method, which interacts with the LLM via `model_client.create()` and executes tools. 

## Development Setup
### Prerequisites and dependencies
The system relies on `autogen_core` and `autogen_ext` for its multi-agent framework and LLM integrations.  Specific LLM providers like DeepSeek and Ollama are supported. 

### Installation steps
While explicit installation steps are not provided, the `backend/mockups/test_functools.py` file suggests `pip install "autogen-agentchat>=0.3.0" "autogen-core>=0.4.0" "autogen-ext[openai]>=0.4.0"` as a starting point for dependencies. 

### Environment configuration
Environment variables, such as `OPENAI_API_KEY`, are used for LLM authentication.  The system uses a `config.json` file for centralized configuration, which can be loaded via `get_config_manager()`.  If `config.json` is missing, a default configuration is created. 

### How to run the project locally
The project has two main entry points:

*   **CLI Application**: The main entry point for the command-line application is `backend/main.py`. It can be run using `python backend/main.py` from the root directory, after installing dependencies.
*   **Web Server**: The project also includes a FastAPI web server that provides a WebSocket interface for chatting with the agent team. To run the server, execute the following command from the `backend` directory:
    ```bash
    uvicorn server:app --host 0.0.0.0 --port 8001
    ```
*   **Frontend Application**: The project includes a React-based chat interface. To run it, navigate to the `frontend` directory and run the following commands:
    ```bash
    # Install dependencies
    npm install

    # Run the development server
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173` by default and will connect to the backend server running on port 8001.

## Code Organization
### Coding standards and conventions
The code generally follows Python's PEP 8 guidelines, with clear docstrings for modules, classes, and functions.  Type hints are used extensively for improved readability and maintainability. 

### File naming patterns
Files are named descriptively, often indicating their purpose or the component they represent (e.g., `main.py`, `factory.py`, `triage_agent.py`). 

### Import/export patterns
Imports are typically grouped by standard library, third-party, and local modules.  Modules export classes and functions that are intended for external use. 

### Component structure (if applicable)
Agents are structured with a base class `AIAgent` providing common functionality, and specialized agents inheriting from it.  The `AgentFactory` centralizes the creation and registration of these agents. 

## Key Features & Implementation
### Main features and how they're implemented
The system's main feature is multi-agent project management.  This is implemented through specialized agents:
*   **Triage Agent**: Routes user requests to appropriate agents.  It uses `transfer_to_*_agent` tools to delegate tasks. 
*   **Project Management Agent**: Guides users through PMI best practices and creates project management plans.  It utilizes the `create_pmi_project_management_plan_tool` to generate markdown plans based on a `Project` data model. 

### Important algorithms or business logic
The core business logic resides within the agents' `handle_task` methods.  This involves sending messages to an LLM, processing its response, and executing tools based on the LLM's output.  Tool execution can involve direct actions or delegation to other agents. 

### API endpoints (if applicable)
The system interacts with several APIs:

*   **LLM APIs**: The system connects to LLM providers like DeepSeek or Ollama through the `ChatCompletionClient`.
*   **OpenTelemetry**: For observability, the system can send tracing data to an OTLP collector endpoint.
*   **WebSocket API**: A FastAPI server provides a WebSocket endpoint for real-time chat with the agent team.
    *   **Endpoint**: `/ws/{session_id}`
    *   **Description**: Establishes a WebSocket connection for a user session. The `session_id` is a unique string that identifies the conversation.
    *   **Usage**: Clients can send chat messages (as text) to the server over the WebSocket connection. The server will broadcast agent responses back to the client.

### Database schema (if applicable)
The system defines data models for project management entities like `Project`, `Epic`, `UserStory`, and `Team` using Pydantic `BaseModel`s.  These models include fields with type annotations, descriptions, and validation rules.  The `backend/models/data_model.yaml` file provides a YAML representation of this schema. 

## Testing Strategy
### Testing frameworks used
The codebase uses `pytest` for testing, with `conftest.py` providing common fixtures and utilities. 

### Test file organization
Test files are located in the `backend/tests/` directory. 

### How to run tests
To run tests, `pytest` would typically be invoked from the command line in the project root. The `conftest.py` file sets up the Python path to include the project root. 

### Testing best practices in this codebase
The `conftest.py` includes utilities for temporary directories, sample data, performance assertion, and cleanup of test files.  It also defines an `auto_cleanup` fixture to ensure cleanup after each test. 

## Build & Deployment
Information regarding build processes, deployment configurations, environment-specific settings, and CI/CD pipelines is not explicitly available in the provided codebase context. <cite/>

## Git Workflow
Information regarding branching strategy, commit message conventions, code review process, and release process is not explicitly available in the provided codebase context. <cite/> However, commit messages indicate a mix of feature additions, bug fixes, and updates by different authors. <cite repo="ogghst/Test_AutoGen2" path="backend/main.py" start="1" end

# Development Partnership and How We Should Partner

We build production code together. I handle implementation details while you guide architecture and catch complexity early.

## Core Workflow: Research → Plan → Implement → Validate

**Start every feature with:** "Let me research the codebase and create a plan before implementing."

1. **Research** - Understand existing patterns and architecture
2. **Plan** - Propose approach and verify with you
3. **Implement** - Build with tests and error handling
4. **Validate** - ALWAYS run formatters, linters, and tests after implementation

## Code Organization

**Keep functions small and focused:**
- If you need comments to explain sections, split into functions
- Group related functionality into clear packages
- Prefer many small files over few large ones

## Architecture Principles

**This is always a feature branch:**
- Delete old code completely - no deprecation needed
- No "removed code" or "added this line" comments - just do it

**Prefer explicit over implicit:**
- Clear function names over clever abstractions
- Obvious data flow over hidden magic
- Direct dependencies over service locators

## Maximize Efficiency

**Parallel operations:** Run multiple searches, reads, and greps in single messages
**Multiple agents:** Split complex tasks - one for tests, one for implementation
**Batch similar work:** Group related file edits together

## Problem Solving

**When stuck:** Stop. The simple solution is usually correct.

**When uncertain:** "Let me ultrathink about this architecture."

**When choosing:** "I see approach A (simple) vs B (flexible). Which do you prefer?"

Your redirects prevent over-engineering. When uncertain about implementation, stop and ask for guidance.

## Testing Strategy

**Match testing approach to code complexity:**
- Complex business logic: Write tests first (TDD)
- Simple CRUD operations: Write code first, then tests
- Hot paths: Add benchmarks after implementation

**Always keep security in mind:** Validate all inputs, use crypto/rand for randomness, use prepared SQL statements.

**Performance rule:** Measure before optimizing. No guessing.

## Progress Tracking

- **Use Todo lists** for task management
- **Clear naming** in all code

Focus on maintainable solutions over clever abstractions.

---
Generated using [Sidekick Dev]({REPO_URL}), your coding agent sidekick.
