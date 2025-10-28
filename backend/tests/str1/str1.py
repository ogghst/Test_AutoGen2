"""
AutoGen Single Agent JSON Generator with Schema Validation
=========================================================

This solution creates a single AutoGen agent that:
1. Takes freeform user prompts
2. Generates structured JSON matching Pydantic schemas
3. Validates against schema
4. Auto-repairs and retries until valid
5. Supports complex graph structures for Neo4j integration

Key Features:
- Single agent handles entire workflow
- Built-in retry loop with error feedback
- Production-ready validation system
- Graph schema support with relationships
- Extensible for Neo4j integration
"""

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
import asyncio
import json
import logging

from autogen_core import Agent, RoutedAgent, MessageContext, message_handler, type_subscription
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_core.models import SystemMessage, UserMessage
from autogen_core import SingleThreadedAgentRuntime

# Configure logging
logging.basicConfig(level=logging.INFO)

# Suppress AutoGen verbose logs
logging.getLogger("autogen_core").setLevel(logging.WARNING)
logging.getLogger("autogen_core.events").setLevel(logging.WARNING)
logging.getLogger("autogen_ext").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# ===== PYDANTIC GRAPH SCHEMA DEFINITIONS =====

class BaseNode(BaseModel):
    """Base class for all graph nodes"""
    id: str = Field(..., description="Unique identifier for the node")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class User(BaseNode):
    """User node in the graph"""
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    role: Literal["admin", "manager", "developer", "stakeholder"] = Field(..., description="User role")
    department: Optional[str] = Field(None, description="User's department")

class Project(BaseNode):
    """Project node in the graph"""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    status: Literal["planning", "active", "on_hold", "completed", "cancelled"] = Field(
        "planning", description="Current project status"
    )
    priority: Literal["low", "medium", "high", "critical"] = Field("medium", description="Project priority")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    budget: Optional[float] = Field(None, description="Project budget in USD")
    
class Team(BaseNode):
    """Team node in the graph"""
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    size: int = Field(..., description="Number of team members", ge=1)

class Issue(BaseNode):
    """Issue/Task node in the graph"""
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    status: Literal["open", "in_progress", "review", "closed"] = Field("open", description="Issue status")
    priority: Literal["low", "medium", "high", "critical"] = Field("medium", description="Issue priority")
    assignee_id: Optional[str] = Field(None, description="ID of assigned user")
    created_by_id: str = Field(..., description="ID of user who created the issue")
    due_date: Optional[datetime] = Field(None, description="Issue due date")

class Milestone(BaseNode):
    """Milestone node in the graph"""
    name: str = Field(..., description="Milestone name")
    description: Optional[str] = Field(None, description="Milestone description")
    due_date: datetime = Field(..., description="Milestone due date")
    status: Literal["planned", "active", "completed", "overdue"] = Field("planned", description="Milestone status")

# ===== RELATIONSHIPS =====

class Relationship(BaseModel):
    """Represents a relationship between two nodes"""
    from_id: str = Field(..., description="Source node ID")
    to_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., description="Type of relationship")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional relationship properties")

# ===== MAIN GRAPH SCHEMA =====

class GraphStructure(BaseModel):
    """Complete graph structure with nodes and relationships"""
    users: List[User] = Field(default_factory=list, description="List of user nodes")
    projects: List[Project] = Field(default_factory=list, description="List of project nodes")
    teams: List[Team] = Field(default_factory=list, description="List of team nodes")
    issues: List[Issue] = Field(default_factory=list, description="List of issue nodes")
    milestones: List[Milestone] = Field(default_factory=list, description="List of milestone nodes")
    relationships: List[Relationship] = Field(default_factory=list, description="List of relationships between nodes")
    
    @field_validator('relationships')
    @classmethod
    def validate_relationships(cls, relationships, info):
        """Validate that relationship IDs reference existing nodes"""
        # Get all node IDs from the model data
        logger.log(logging.INFO, f"Validating relationships: {relationships}")
        all_ids = set()
        if hasattr(info, 'data'):
            for node_type in ['users', 'projects', 'teams', 'issues', 'milestones']:
                if node_type in info.data:
                    all_ids.update(node.id for node in info.data[node_type])
        
        # Validate relationship references
        for rel in relationships:
            if rel.from_id not in all_ids:
                raise ValueError(f"Relationship from_id '{rel.from_id}' not found in graph nodes")
            if rel.to_id not in all_ids:
                raise ValueError(f"Relationship to_id '{rel.to_id}' not found in graph nodes")
        
        return relationships

# ===== VALIDATION MESSAGES AND RESPONSES =====

class GenerateStructuredJSONRequest(BaseModel):
    """Request message for JSON generation"""
    user_prompt: str
    max_retries: int = 3

class ValidationResult(BaseModel):
    """Result of JSON validation"""
    is_valid: bool
    json_data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    parsed_graph: Optional[GraphStructure] = None

class StructuredJSONResponse(BaseModel):
    """Response containing validated JSON"""
    success: bool
    json_data: Optional[Dict[str, Any]] = None
    graph_structure: Optional[GraphStructure] = None
    validation_attempts: int = 0
    error_message: Optional[str] = None

class JSONGenerationResult(BaseModel):
    """Result message for JSON generation"""
    request_id: str
    response: StructuredJSONResponse

# ===== VALIDATION TOOL =====

class JSONValidationTool:
    """Tool for validating JSON against Pydantic schema"""
    
    @staticmethod
    def validate_json_against_schema(json_string: str) -> ValidationResult:
        """
        Validates JSON string against GraphStructure schema
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        try:
            logger.log(logging.INFO, f"Validating JSON string: {json_string}")
            # Parse JSON
            json_data = json.loads(json_string)
            
            # Validate against Pydantic schema
            graph_structure = GraphStructure(**json_data)
            
            return ValidationResult(
                is_valid=True,
                json_data=json_data,
                parsed_graph=graph_structure,
                errors=[]
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"JSON parsing error: {str(e)}"]
            )
            
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error['loc'])
                error_messages.append(f"Field '{loc}': {error['msg']}")
            
            return ValidationResult(
                is_valid=False,
                errors=error_messages
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unexpected validation error: {str(e)}"]
            )

# ===== MAIN AGENT =====

@type_subscription(topic_type="str")
class StructuredJSONAgent(RoutedAgent):
    """
    Single AutoGen agent that handles the complete JSON generation and validation workflow.
    
    This agent:
    1. Receives freeform user prompts
    2. Generates structured JSON matching the GraphStructure schema
    3. Validates the JSON using built-in validation
    4. Auto-repairs and retries until schema compliance is achieved
    5. Returns validated JSON suitable for Neo4j integration
    """
    
    def __init__(self, model_client: OpenAIChatCompletionClient):
        super().__init__("Structured JSON Generation Agent")
        self.model_client = model_client
        self.validator = JSONValidationTool()
        
        # Register validation tool
        self.validation_tool = FunctionTool(
            self.validator.validate_json_against_schema,
            description="Validates JSON string against the GraphStructure schema"
        )
        
    def _get_system_prompt(self) -> str:
        """Generate comprehensive system prompt with schema and instructions"""
        schema_json = json.dumps(GraphStructure.model_json_schema(), indent=2)
        
        return f"""
You are a specialized JSON generation agent that creates structured data matching a specific Pydantic schema.

CRITICAL INSTRUCTIONS:
1. ALWAYS generate JSON that strictly matches the provided GraphStructure schema
2. ALWAYS validate your JSON using the validation tool before returning results
3. If validation fails, analyze the error messages and fix the JSON automatically
4. Retry until validation succeeds (maximum 3 attempts)
5. Generate realistic, coherent data that makes business sense

SCHEMA TO MATCH:
{schema_json}

GRAPH STRUCTURE RULES:
- Users can be assigned to projects via relationships
- Projects have teams via relationships  
- Issues are created by users and can be assigned to users
- Issues belong to projects via relationships
- Milestones belong to projects via relationships
- All nodes must have unique IDs
- Relationships must reference valid node IDs

VALIDATION WORKFLOW:
1. Generate JSON matching the schema
2. Call validate_json_against_schema tool
3. If invalid, analyze errors and regenerate
4. Repeat until valid (max 3 attempts)

RESPONSE FORMAT:
Always return the final validated JSON as a properly formatted JSON object.

EXAMPLE RELATIONSHIPS:
- {{"from_id": "user_1", "to_id": "project_1", "relationship_type": "ASSIGNED_TO"}}
- {{"from_id": "project_1", "to_id": "team_1", "relationship_type": "HAS_TEAM"}}  
- {{"from_id": "issue_1", "to_id": "user_1", "relationship_type": "CREATED_BY"}}
- {{"from_id": "issue_1", "to_id": "project_1", "relationship_type": "BELONGS_TO"}}
"""

    @message_handler
    async def handle_generate_request(
        self, 
        message: GenerateStructuredJSONRequest, 
        ctx: MessageContext
    ) -> StructuredJSONResponse:
        """
        Main message handler that orchestrates the complete workflow
        
        Args:
            message: Request containing user prompt and configuration
            ctx: Message context from AutoGen
            
        Returns:
            StructuredJSONResponse with validated JSON or error details
        """
        logger.info(f"Processing request: {message.user_prompt}")
        
        validation_attempts = 0
        max_retries = message.max_retries
        
        # Initial generation prompt
        generation_prompt = f"""
Based on this user request: "{message.user_prompt}"

Generate a complete JSON structure that matches the GraphStructure schema. 

Consider what entities and relationships would be needed:
- If it's about a project charter: include project, team, users, milestones
- If it's about issues: include issues, users, projects, assignments
- If it's about teams: include team, users, projects, roles

Create realistic, coherent data with proper relationships between entities.
Generate the JSON now:
"""
        
        while validation_attempts < max_retries:
            validation_attempts += 1
            logger.info(f"Generation attempt {validation_attempts}/{max_retries}")
            
            try:
                # Try LLM call with timeout, fallback to mock if it fails
                logger.info(f"Attempting LLM API call for attempt {validation_attempts}")
                logger.info(f"  System message: {self._get_system_prompt()}")
                logger.info(f"  Generation prompt: {generation_prompt}")
                
                try:
                    response = await self.model_client.create(
                            messages=[
                                SystemMessage(content=self._get_system_prompt()),
                                UserMessage(content=generation_prompt, source="User")
                            ],
                            tools=[self.validation_tool],
                            cancellation_token=ctx.cancellation_token
                        )
                    
                    
                    logger.info(f"LLM API call successful for attempt {validation_attempts}")
                    
                    # Extract generated JSON
                    generated_content = response.content
                    logger.info(f"Response content type: {type(generated_content)}")
                    
                    if isinstance(generated_content, list):
                        if generated_content:
                            first_item = generated_content[0]
                            if hasattr(first_item, 'text'):
                                generated_content = first_item.text
                            elif hasattr(first_item, 'content'):
                                generated_content = first_item.content
                            else:
                                generated_content = str(first_item)
                        else:
                            generated_content = ""
                    elif hasattr(generated_content, 'text'):
                        generated_content = generated_content.text
                    elif hasattr(generated_content, 'content'):
                        generated_content = generated_content.content
                    else:
                        generated_content = str(generated_content)
                    
                    logger.info(f"Extracted content: {generated_content[:200]}...")
                    json_text = self._extract_json_from_response(generated_content)
                    logger.info(f"Extracted JSON from LLM response")
                    
                except asyncio.TimeoutError:
                    logger.error(f"LLM API call timed out after 30 seconds for attempt {validation_attempts}")
                    raise Exception(f"LLM API call timed out after 30 seconds")
                    
                except Exception as e:
                    logger.error(f"LLM API call failed: {str(e)}")
                    raise Exception(f"LLM API call failed: {str(e)}")
                
                # Validate the generated JSON
                logger.info(f"Validating JSON against schema")
                validation_result = self.validator.validate_json_against_schema(json_text)
                
                if validation_result.is_valid:
                    logger.info("JSON validation successful!")
                    response = StructuredJSONResponse(
                        success=True,
                        json_data=validation_result.json_data,
                        graph_structure=validation_result.parsed_graph,
                        validation_attempts=validation_attempts
                    )
                    
                    logger.info(f"Sending result to result handler")
                    # Send the result to result handler
                    result = JSONGenerationResult(
                        request_id=f"req_{validation_attempts}",
                        response=response
                    )
                    from autogen_core import AgentId
                    result_agent_id = AgentId("result", "default")
                    await self.send_message(result, result_agent_id)
                    return "JSON generation completed successfully"
                else:
                    # Validation failed - prepare retry prompt with error feedback
                    error_details = "\n".join(validation_result.errors)
                    logger.warning(f"Validation failed (attempt {validation_attempts}): {error_details}")
                    
                    generation_prompt = f"""
The previous JSON was INVALID due to these errors:
{error_details}

Original request: "{message.user_prompt}"

Please fix these specific issues and generate a corrected JSON that matches the GraphStructure schema.

Previous JSON that failed:
{json_text}

Generate the corrected JSON now:
"""
                    
            except Exception as e:
                logger.error(f"Error during generation attempt {validation_attempts}: {str(e)}")
                if validation_attempts == max_retries:
                    response = StructuredJSONResponse(
                        success=False,
                        validation_attempts=validation_attempts,
                        error_message=f"Failed after {max_retries} attempts. Last error: {str(e)}"
                    )
                    
                    # Send the error result to result handler
                    result = JSONGenerationResult(
                        request_id=f"req_{validation_attempts}",
                        response=response
                    )

                    from autogen_core import AgentId
                    result_agent_id = AgentId("result", "default")
                    await self.send_message(result, result_agent_id)
                    return f"JSON generation failed after {max_retries} attempts"
                
                generation_prompt = f"""
An error occurred: {str(e)}

Original request: "{message.user_prompt}"

Please generate a valid JSON structure that matches the GraphStructure schema.
Focus on creating syntactically correct JSON with all required fields.

Generate the JSON now:
"""
        
        # If we reach here, all retries failed
        response = StructuredJSONResponse(
            success=False,
            validation_attempts=validation_attempts,
            error_message=f"Failed to generate valid JSON after {max_retries} attempts"
        )
        
        # Send the final error result to result handler
        result = JSONGenerationResult(
            request_id=f"req_{validation_attempts}",
            response=response
        )
        from autogen_core import AgentId
        result_agent_id = AgentId("result", "default")
        await self.send_message(result, result_agent_id)
        return f"JSON generation failed after {max_retries} attempts"
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """
        Extract JSON from LLM response, handling markdown formatting and other artifacts
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Cleaned JSON string
        """
        logger.log(logging.INFO, f"Extracting JSON from response: {response_text}")
        # Remove markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end]
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end]
        
        # Find JSON object boundaries
        start_idx = response_text.find("{")
        if start_idx == -1:
            return response_text.strip()
        
        # Find matching closing brace
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(response_text)):
            if response_text[i] == "{":
                brace_count += 1
            elif response_text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx != -1:
            return response_text[start_idx:end_idx].strip()
        else:
            return response_text[start_idx:].strip()



# ===== PRODUCTION USAGE =====

@type_subscription(topic_type="result")
class ResultHandler(RoutedAgent):
    """Simple agent to handle and display results"""
    
    def __init__(self):
        super().__init__("Result Handler")
        self.results = []
    
    @message_handler
    async def handle_result(self, message: JSONGenerationResult, ctx: MessageContext) -> str:
        """Handle JSON generation results"""
        logger.info(f"ResultHandler received message: {message.request_id}")
        self.results.append(message)
        print(f"✅ Received result for request {message.request_id}")
        if message.response.success:
            print(f"   Success! Generated {len(message.response.json_data.get('users', []))} users, "
                  f"{len(message.response.json_data.get('projects', []))} projects")
            logger.info(f"Successfully processed request {message.request_id}")
        else:
            print(f"   Failed: {message.response.error_message}")
            logger.warning(f"Request {message.request_id} failed: {message.response.error_message}")
        print()
        return f"Processed result for request {message.request_id}"

async def main():
    """
    Main function demonstrating production usage of the agent
    """
    
    # Initialize OpenAI client (replace with your actual configuration)
    model_client = OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key="sk-9a4206f76b4a466095d6b85b859c6a85",  # Use environment variable in production
        base_url="https://api.deepseek.com",
        model_info={
            "family": "deepseek",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True
        }
    )
    
    # Create runtime
    runtime = SingleThreadedAgentRuntime()
    
    # Create result handler
    result_handler = ResultHandler()
    
    # Register the agents
    await StructuredJSONAgent.register(runtime, type="str",
                                 factory=lambda: StructuredJSONAgent(model_client))
    await ResultHandler.register(runtime, type="result", factory=lambda: ResultHandler())
    
    # Start the runtime
    runtime.start()
    
    try:
        # Example requests - start with just one for debugging
        test_prompts = [
            "Create a simple project with 2 users and 1 team"
        ]
        
        print("=== PRODUCTION USAGE EXAMPLES ===")
        print()
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"Example {i}: {prompt}")
            print("-" * 50)
            
            request = GenerateStructuredJSONRequest(
                user_prompt=prompt,
                max_retries=3
            )
            
            # Send message directly to the agent
            from autogen_core import AgentId
            agent_id = AgentId("str", "default")
            await runtime.send_message(request, agent_id)
            
            # Wait a bit for processing
            await asyncio.sleep(5)
            
            print("Message sent to agent for processing")
            print()
    
    finally:
        # Stop the runtime
        await runtime.stop()

if __name__ == "__main__":
    # Run the retry loop demonstration
    #asyncio.run(demonstrate_retry_loop())
    
    # Uncomment to run production examples
    asyncio.run(main())