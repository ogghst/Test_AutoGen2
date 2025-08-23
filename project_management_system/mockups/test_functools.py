"""
AutoGen Project Info Extractor using Function Tools

Requirements:
  pip install "autogen-agentchat>=0.3.0" "autogen-core>=0.4.0" "autogen-ext[openai]>=0.4.0"
  # Or: pip install autogen-agentchat autogen-core autogen-ext

Environment:
  export OPENAI_API_KEY=...  # or configure a different model client per AutoGen docs

What it does:
  - Defines a FunctionTool `save_project_info` with clear, typed parameters.
  - Builds a minimal tool-enabled agent that reads unstructured user text and
    extracts project information by calling the tool exactly once.
  - Persists extracted entries to a local JSONL file for later use (e.g., GraphRAG).

Reference:
  This follows the AutoGen Tools guide:
  https://microsoft.github.io/autogen/stable/user-guide/core-user-guide/components/tools.html
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Literal
from typing_extensions import Annotated

from pyld import jsonld

from autogen_core import (
    AgentId,
    FunctionCall,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
    CancellationToken,
)
from autogen_core.models import (
    ChatCompletionClient,
    LLMMessage,
    AssistantMessage,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
    SystemMessage,
    UserMessage,
    ModelInfo,
)
from autogen_core.tools import FunctionTool, Tool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

from urllib.parse import urljoin

# -----------------------------
# Logging configuration
# -----------------------------

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('project_extractor.log')  # File handler
    ]
)
logger = logging.getLogger(__name__)

# -----------------------------
# Tool definition
# -----------------------------

DATA_PATH = Path("./extracted_project_info.json")
JSONLD_PATH = Path("./extracted_project_info.jsonld")


def create_basic_context(json_data, base_vocab="http://schema.org/"):
    """
    Generate a basic context mapping JSON keys to a vocabulary
    """
    def extract_keys(obj, keys=None):
        if keys is None:
            keys = set()
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not key.startswith('@'):  # Skip JSON-LD keywords
                    keys.add(key)
                extract_keys(value, keys)
        elif isinstance(obj, list):
            for item in obj:
                extract_keys(item, keys)
        
        return keys
    
    # Extract all unique keys
    keys = extract_keys(json_data)
    
    # Create context mapping
    context = {}
    for key in keys:
        context[key] = urljoin(base_vocab, key)
    
    return {"@context": context}

@dataclass
class ProjectInfo:
    """A complete project information container with serialization capabilities."""
    title: Annotated[str, "Project title. Keep it short."]
    description: Annotated[str, "One-paragraph summary of the project scope and goals."]
    stakeholders: Annotated[List[str], "List of stakeholder names or roles (e.g., 'PM', 'QA lead')."]
    start_date: Annotated[Optional[str], "Start date in ISO 8601 (YYYY-MM-DD) or None if unknown."]
    due_date: Annotated[Optional[str], "Due/target date in ISO 8601 (YYYY-MM-DD) or None if unknown."]
    requirements: Annotated[List[Requirement], "List of key requirements or deliverables"]
    risks: Annotated[Optional[List[str]], "Known risks or blockers, or None if not provided."]
    budget: Annotated[Optional[float], "Estimated budget amount (numeric) or None if unknown."]
    currency: Annotated[Optional[str], "Currency code like 'EUR', 'USD' or None."]
    priority: Annotated[Optional[Literal["low", "medium", "high"]], "Overall priority if stated."]
    created_at: Annotated[Optional[str], "Date and time the project info was created. Default to current date and time."]
    updated_at: Annotated[Optional[str], "Date and time the project info was last updated. Default to current date and time."]
    
    def __post_init__(self):
        """Set default timestamps if not provided."""
        from datetime import datetime
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def to_dict(self) -> dict:
        """Convert the ProjectInfo to a dictionary for JSON serialization."""
        logger.info(f"Converting ProjectInfo to dict: {self.title}")
        
        # Convert requirements to serializable format
        serialized_requirements = []
        for req in self.requirements:
            if isinstance(req, Requirement):
                serialized_requirements.append(req.to_dict())
            elif isinstance(req, dict):
                serialized_requirements.append(req)
            else:
                logger.warning(f"Unexpected requirement format: {type(req)}, converting to string")
                serialized_requirements.append(str(req))
        
        return {
            "title": self.title,
            "description": self.description,
            "stakeholders": self.stakeholders,
            "start_date": self.start_date,
            "due_date": self.due_date,
            "requirements": serialized_requirements,
            "risks": self.risks,
            "budget": self.budget,
            "currency": self.currency,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProjectInfo":
        """Create a ProjectInfo instance from a dictionary."""
        logger.info(f"Creating ProjectInfo from dict: {data.get('title', 'Unknown')}")
        
        # Convert requirements back to Requirement objects if they're dicts
        requirements = []
        for req_data in data.get("requirements", []):
            if isinstance(req_data, dict):
                try:
                    requirements.append(Requirement.from_dict(req_data))
                except Exception as e:
                    logger.warning(f"Failed to convert requirement dict to Requirement object: {e}")
                    requirements.append(req_data)
            else:
                requirements.append(req_data)
        
        return cls(
            title=data["title"],
            description=data["description"],
            stakeholders=data["stakeholders"],
            start_date=data.get("start_date"),
            due_date=data.get("due_date"),
            requirements=requirements,
            risks=data.get("risks"),
            budget=data.get("budget"),
            currency=data.get("currency"),
            priority=data.get("priority"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    def to_json(self) -> str:
        """Convert the ProjectInfo to a JSON string."""
        logger.info(f"Converting ProjectInfo to JSON: {self.title}")
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ProjectInfo":
        """Create a ProjectInfo instance from a JSON string."""
        logger.info(f"Creating ProjectInfo from JSON string")
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class Requirement:
    """A requirement is a key deliverable or feature of the project."""
    description: Annotated[str, "Description of the requirement."]
    priority: Annotated[Literal["low", "medium", "high"], "Priority level of the requirement."]
    status: Annotated[Literal["todo", "in_progress", "done"], "Current status of the requirement."]
    assignee: Annotated[Optional[str], "Name of the person assigned to the requirement."]
    due_date: Annotated[Optional[str], "Due date in ISO 8601 (YYYY-MM-DD) or None if unknown."]
    created_at: Annotated[str, "Date and time the requirement was created. Default to current date and time."]
    updated_at: Annotated[str, "Date and time the requirement was last updated. Default to current date and time."]
    
    def to_dict(self) -> dict:
        """Convert the Requirement to a dictionary for JSON serialization."""
        logger.info(f"Converting Requirement to dict: {self}")
        return {
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Requirement":
        """Create a Requirement instance from a dictionary."""
        logger.info(f"Creating Requirement from dict: {data}")
        return cls(
            description=data["description"],
            priority=data["priority"],
            status=data["status"],
            assignee=data.get("assignee"),
            due_date=data.get("due_date"),
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def to_json(self) -> str:
        """Convert the Requirement to a JSON string."""
        logger.info(f"Converting Requirement to JSON: {self}")
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Requirement":
        """Create a Requirement instance from a JSON string."""
        logger.info(f"Creating Requirement from JSON: {json_str}")
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Requirement(description='{self.description}', priority='{self.priority}', status='{self.status}')"


async def save_project_info(
    projectInfo: Annotated[ProjectInfo, "Project information to save."]
) -> str:
    """Persist a structured snapshot of project information to JSON and return a receipt string.

    The function assumes inputs are already extracted by the LLM. If some data
    is missing in the source text, pass None or an empty list, as appropriate.
    """
    logger.info(f"Starting to save project info for: {projectInfo.title}")
    logger.debug(f"Project details - Description: {projectInfo.description[:100]}...")
    logger.debug(f"Stakeholders: {projectInfo.stakeholders}")
    logger.debug(f"Budget: {projectInfo.budget} {projectInfo.currency}")
    logger.debug(f"Requirements count: {len(projectInfo.requirements)}")
    
    
    entry = projectInfo.to_dict()
    
    # Append to a local JSON file for easy downstream consumption.
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing project data to: {DATA_PATH}")
    
    try:
        with DATA_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, indent=4) + "\n")
        logger.info(f"Successfully saved project info for: {projectInfo.title}")
        
        PROJECT_JSONLD_CONTEXT = create_basic_context(entry)
        
        # Merge context with data
        jsonld_data = jsonld.flatten({**PROJECT_JSONLD_CONTEXT, **entry})
        with JSONLD_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(jsonld_data, ensure_ascii=False, indent=4) + "\n")
        logger.info(f"Successfully saved project info for: {projectInfo.title} in JSON-LD format")
        
        return "Saved project info entry with title: {}".format(projectInfo.title)
    except Exception as e:
        logger.error(f"Failed to save project info for {projectInfo.title}: {e}")
        raise

save_project_info_tool: Tool = FunctionTool(
    save_project_info,
    description=(
        "Extracted-Info Sink: Call this exactly ONCE per user request to persist a structured "
        "snapshot of project information parsed from the user's unstructured text. If a field is "
        "not mentioned, use None (or an empty list)."
    ),
)

# -----------------------------
# Minimal tool-enabled agent
# -----------------------------

SYSTEM_INSTRUCTIONS = (
    "You are a Project Info Extractor. Read the user's unstructured text and extract "
    "key project fields. IMPORTANT: Do not invent facts. If a field is missing, "
    "pass None or an empty list. Then call the tool `save_project_info` exactly once with your best "
    "extracted values. If dates are ambiguous (e.g., 'next month'), infer ISO format when safe; "
    "otherwise use None. Return a concise confirmation to the user after the tool result."
)

@dataclass
class Message:
    content: str

class ProjectExtractorAgent(RoutedAgent):
    """A minimal agent that invokes a FunctionTool to persist extracted info."""

    def __init__(self, model_client: ChatCompletionClient, tools: List[Tool]):
        super().__init__("project_extractor")
        logger.info("Initializing ProjectExtractorAgent")
        self._system_messages: List[LLMMessage] = [SystemMessage(content=SYSTEM_INSTRUCTIONS)]
        self._model_client = model_client
        self._tools = tools
        logger.info(f"Agent initialized with {len(tools)} tools")

    @message_handler
    async def handle_user_message(self, message: Message, ctx: MessageContext) -> Message:
        logger.info(f"Received user message: {message.content[:100]}...")
        
        # Build session history for the model
        session: List[LLMMessage] = self._system_messages + [UserMessage(content=message.content, source="user")]
        logger.debug(f"Built session with {len(session)} messages")

        # Ask the model to produce a tool call with extracted fields
        logger.info("Requesting model to extract project information and produce tool calls")
        create_result = await self._model_client.create(
            messages=session,
            tools=self._tools,
            cancellation_token=ctx.cancellation_token,
        )
        logger.debug(f"Model response type: {type(create_result.content)}")

        # If no tool call was produced, just return the model's text
        if isinstance(create_result.content, str):
            logger.warning("Model did not produce tool calls, returning text response")
            return Message(content=create_result.content)

        # Ensure we received function calls
        assert isinstance(create_result.content, list) and all(
            isinstance(call, FunctionCall) for call in create_result.content
        )
        logger.info(f"Model produced {len(create_result.content)} function calls")

        #return Message(content=create_result.content)

        # Keep the tool-call message in session
        session.append(AssistantMessage(content=create_result.content, source="assistant"))

        # Execute all tool calls (we ask the model to call exactly once)
        logger.info("Executing tool calls")
        results = await asyncio.gather(
            *[self._execute_tool_call(call, ctx.cancellation_token) for call in create_result.content]
        )
        logger.info(f"Executed {len(results)} tool calls")

        # Provide tool execution results back to the model for a final confirmation reply
        session.append(FunctionExecutionResultMessage(content=results))
        logger.info("Requesting final confirmation from model")
        final = await self._model_client.create(messages=session, cancellation_token=ctx.cancellation_token)
        assert isinstance(final.content, str)
        logger.info("Final response received from model")
        return Message(content=final.content)

    async def _execute_tool_call(self, call: FunctionCall, cancellation_token: CancellationToken) -> FunctionExecutionResult:
        logger.info(f"Executing tool call: {call.name}")
        logger.debug(f"Tool call arguments: {call.arguments}")
        
        tool = next((t for t in self._tools if t.name == call.name), None)
        if tool is None:
            logger.error(f"Tool not found: {call.name}")
            raise ValueError(f"Tool not found: {call.name}")
        
        try:
            args = json.loads(call.arguments)
            logger.debug(f"Parsed arguments: {args}")
            result = await tool.run_json(args, cancellation_token)
            logger.info(f"Tool {call.name} executed successfully")
            return FunctionExecutionResult(
                call_id=call.id,
                content=tool.return_value_as_string(result),
                is_error=False,
                name=tool.name,
            )
        except Exception as e:
            logger.error(f"Tool {call.name} execution failed: {e}")
            return FunctionExecutionResult(call_id=call.id, content=str(e), is_error=True, name=tool.name)

# -----------------------------
# Helper functions
# -----------------------------

def create_sample_requirement(
    description: str,
    priority: Literal["low", "medium", "high"] = "medium",
    status: Literal["todo", "in_progress", "done"] = "todo",
    assignee: Optional[str] = None,
    due_date: Optional[str] = None
) -> Requirement:
    """Create a sample requirement with current timestamps."""
    from datetime import datetime
    
    now = datetime.now().isoformat()
    return Requirement(
        description=description,
        priority=priority,
        status=status,
        assignee=assignee,
        due_date=due_date,
        created_at=now,
        updated_at=now
    )

# -----------------------------
# Bootstrap & demo
# -----------------------------

@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API"""
    api_key: str = "*** redacted ***"
    model: str = "deepseek-chat"
    api_url: str = "https://api.deepseek.com"
    model_info: ModelInfo = field(default_factory=lambda: {
                "family": "deepseek",
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True
            })

@dataclass
class OllamaConfig:
    """Configuration for Ollama"""
    base_url: str = "http://172.17.0.1:11434"
    model: str = "gemma3:4b"
    model_info: ModelInfo = field(default_factory=lambda: {
                "family": "ollama",
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True
            })


async def main() -> None:
    logger.info("Starting Project Info Extractor application")

    # Choose a model client; OpenAI GPT-4o-mini supports tool calls.
    #model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    deepseek_config = DeepSeekConfig()
    ollama_config = OllamaConfig()

    logger.info(f"Using DeepSeek model: {deepseek_config.model}")
    model_client = OpenAIChatCompletionClient(
                model=deepseek_config.model,
                api_key=deepseek_config.api_key,
                base_url=deepseek_config.api_url,
                model_info=deepseek_config.model_info
            )

    #model_client =  OllamaChatCompletionClient(
    #        model=ollama_config.model,
    #        base_url=ollama_config.base_url,
    #        model_info=ollama_config.model_info
    #    )

    logger.info("Initializing agent runtime")
    runtime = SingleThreadedAgentRuntime()

    # Register the tool-enabled agent
    logger.info("Registering ProjectExtractorAgent")
    await ProjectExtractorAgent.register(
        runtime,
        "project_extractor",
        lambda: ProjectExtractorAgent(model_client=model_client, tools=[save_project_info_tool]),
    )

    # Start the runtime
    logger.info("Starting agent runtime")
    runtime.start()

    # Example unstructured text from a user
    #user_text = (
    #    "We're kicking off Project Atlas to migrate our on-prem ERP to the cloud. "
    #    "Giulia Rossi (PM) and Marco Bianchi (CTO) are the main stakeholders. Budget around 120000 EUR. "
    #    "We aim to start on 2025-09-01 and finish by 2026-03-31. Key requirements: zero downtime migration, "
    #    "SSO with Azure AD, and training for 50 users. Risks: data quality issues and tight timeline. Priority is high."
    #)
    user_text = """Project Overview
Project Name: Project Atlas
Project Goal: To successfully migrate the company's on-premise Enterprise Resource Planning (ERP) system to a cloud-based solution. This initiative is critical for modernizing our infrastructure, improving scalability, and enhancing data accessibility.

Key Project Details
Primary Stakeholders:

Giulia Rossi (Project Manager): Responsible for day-to-day project execution, team coordination, and stakeholder communication.

Marco Bianchi (Chief Technology Officer): Serves as the executive sponsor, providing high-level technical guidance and strategic oversight.

Budget:

A provisional budget of 120,000 EUR has been allocated. This covers licensing fees, migration services, training, and contingency. A detailed breakdown and a more granular budget will be developed in the project's planning phase.

Timeline:

Start Date: 2025-09-01

End Date: 2026-03-31

Total Duration: 7 months. This is a tight timeline, requiring careful planning and execution to meet the deadline.

Priority:

This project has a high priority and is considered a strategic imperative for the company's long-term growth and operational efficiency.

Detailed Scope & Requirements
Functional Requirements:
- Zero-Downtime Migration: The migration process must be executed without any disruption to critical business operations. A phased or incremental migration strategy will be explored to minimize impact.
- Single Sign-On (SSO) with Azure AD: The new cloud ERP must seamlessly integrate with our existing Azure Active Directory for user authentication and authorization. This will simplify user access and improve security.
- User Training: Comprehensive training must be provided for a minimum of 50 users to ensure a smooth transition and full adoption of the new system. This will include creating training materials, conducting workshops, and providing post-launch support.

Technical Requirements:
- The cloud ERP solution must meet industry standards for security and data privacy.
- Data must be migrated accurately and completely from the old system to the new one.
- The new system must be scalable to accommodate future business growth.

Risks and Mitigations

Risk: Data quality issues from the legacy on-premise system.
Mitigation: A thorough data audit and cleansing process will be conducted before the migration begins. This will involve working closely with business units to identify and resolve data inconsistencies.

Risk: Tight project timeline, potentially leading to rushed decisions or incomplete work.
Mitigation: An agile methodology will be adopted to allow for quick iteration and adaptation. Regular communication and clear milestone tracking will be crucial to stay on schedule. A dedicated project team will be established to focus solely on this initiative.

Risk: User resistance to the new system.
Mitigation: The project team will implement a change management plan that includes early communication, user involvement in testing, and accessible training resources to ensure a positive transition.

Success Metrics
Project success will be measured by:

Completion within the defined budget and timeline.

Successful migration with no unplanned business interruptions.

Full integration of SSO with Azure AD.

Completion of training for all 50 users.

Positive feedback from key stakeholders and end-users after the go-live.

"""

    logger.info("Sending user message to agent")
    logger.info(f"User text: {user_text}")
    
    agent_id = AgentId("project_extractor", "default")
    response = await runtime.send_message(Message(user_text), agent_id)
    logger.info("Received response from agent")
    print("Agent:", response.content)

    logger.info("Stopping agent runtime")
    await runtime.stop()
    logger.info("Closing model client")
    await model_client.close()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PROJECT INFO EXTRACTOR STARTING")
    logger.info("=" * 60)
    
    try:
        asyncio.run(main())
        logger.info("Application completed successfully")
    except Exception as e:
        logger.error(f"Application failed with error: {e}", exc_info=True)
        raise
    finally:
        logger.info("=" * 60)
        logger.info("PROJECT INFO EXTRACTOR SHUTDOWN")
        logger.info("=" * 60)
