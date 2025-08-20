# Handoffs Multi-Agent Pattern Implementation

This implementation demonstrates the **Handoffs** multi-agent design pattern using Microsoft AutoGen Core, adapted for project management scenarios.

## Overview

The Handoffs pattern allows agents to delegate tasks to other specialized agents using special tool calls. This creates a flexible, scalable system where agents can focus on their specific domains while seamlessly transferring users to the most appropriate agent for their needs.

## Architecture

### Agent Types

1. **Triage Agent** - The entry point that understands user requests and routes them to appropriate specialized agents
2. **Planning Agent** - Handles project planning, requirements gathering, and project timelines
3. **Execution Agent** - Manages task execution and project deliverables
4. **Quality Agent** - Conducts quality assurance and project reviews
5. **Human Agent** - Handles complex requests requiring human intervention
6. **User Agent** - Manages user sessions and coordinates communication

### Communication Flow

```
User → User Agent → Triage Agent → Specialized Agent (Planning/Execution/Quality)
                                    ↓
                              Human Agent (if needed)
```

## Key Features

- **Event-driven communication** using pub-sub pattern
- **Automatic task delegation** based on user intent
- **Seamless agent handoffs** with context preservation
- **Human-in-the-loop** escalation for complex cases
- **Modular agent design** for easy extension

## How It Works

1. **User Login**: Creates a new session and starts conversation with Triage Agent
2. **Request Analysis**: Triage Agent analyzes user intent and determines the best agent
3. **Task Delegation**: Uses transfer tools to hand off to specialized agents
4. **Context Preservation**: Full conversation history is maintained during transfers
5. **Response Handling**: Specialized agents process requests and can transfer back if needed

## Tools

### Transfer Tools (Delegate Tools)
- `transfer_to_planning` - Routes to Planning Agent
- `transfer_to_execution` - Routes to Execution Agent  
- `transfer_to_quality` - Routes to Quality Agent
- `transfer_back_to_triage` - Returns to Triage Agent
- `escalate_to_human` - Escalates to Human Agent

### Functional Tools
- `create_project_plan` - Creates project plans
- `execute_project_task` - Executes project tasks
- `review_project_quality` - Reviews project quality

## Usage

### Running the System

```bash
cd project_management_system/POC
python handoffs_pattern.py
```

### Example Conversation Flow

1. **User**: "I want to create a new project plan"
2. **Triage Agent**: Analyzes request and transfers to Planning Agent
3. **Planning Agent**: Helps create project plan, asks clarifying questions
4. **User**: Provides project details
5. **Planning Agent**: Creates plan using `create_project_plan` tool
6. **User**: "Now I want to execute some tasks"
7. **Planning Agent**: Transfers back to Triage Agent
8. **Triage Agent**: Transfers to Execution Agent
9. **Execution Agent**: Helps execute tasks using `execute_project_task` tool

### Exiting

Type "exit" to end the session.

## Benefits

- **Scalability**: Easy to add new specialized agents
- **Maintainability**: Each agent has a single responsibility
- **Flexibility**: Dynamic routing based on user needs
- **User Experience**: Seamless transitions between agents
- **Extensibility**: Simple to add new tools and capabilities

## Technical Implementation

- **AutoGen Core**: Uses the latest AutoGen Core API for event-driven agents
- **Async/Await**: Full async support for better performance
- **Type Safety**: Comprehensive type hints and validation
- **Error Handling**: Robust error handling and fallback mechanisms
- **Message Routing**: Efficient pub-sub message routing system

## Customization

### Adding New Agents

1. Create a new agent class inheriting from `AIAgent`
2. Define appropriate system message and tools
3. Register the agent with the runtime
4. Add transfer tools for routing to/from the new agent

### Adding New Tools

1. Create async function for the tool
2. Create `FunctionTool` instance with proper schema
3. Add to appropriate agent's tools list
4. Update agent's system message if needed

## Dependencies

- `autogen_core` - Core AutoGen functionality
- `autogen_ext` - Extended models and clients
- `pydantic` - Data validation and serialization
- `asyncio` - Asynchronous programming support

## Future Enhancements

- **Persistent Storage**: Save conversation history and agent states
- **Advanced Routing**: ML-based routing decisions
- **Multi-language Support**: Internationalization for global teams
- **Analytics**: Track agent performance and user satisfaction
- **Integration**: Connect with external project management tools
