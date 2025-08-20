from typing import Optional, List, Dict, Any
import re
from datetime import datetime

from .base_agent import BaseProjectAgent, DeepSeekConfig, OllamaConfig, LLMConnectionError
from typing import Union
from models.data_models import AgentConfig, DeepSeekConfig, OllamaConfig, AgentRole, ProjectContext
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


class ProjectManagerAgent(BaseProjectAgent):
    """Project Manager - Main Orchestrator
    
    This agent coordinates project workflow and manages stakeholder communication. 
    It can handle the following user intents:
    
    **Project Initialization:**
    - "I want to create a new project about..."
    - "Initialize a project for..."
    - "We need to build..."
    - "Start a project regarding..."
    
    **Project Management:**
    - "What's the status of my project?"
    - "Show me project updates"
    - "How is the project progressing?"
    
    **Requirements Gathering:**
    - "Let's gather requirements"
    - "Start requirements phase"
    - "What requirements do we need?"
    
    **Project Planning:**
    - "Create project plan"
    - "Let's plan the project"
    - "Show me the project plan"
    
    **System Control:**
    - "Restart project"
    - "Start over"
    - "New project"
    
    The agent analyzes user intent from natural language and routes to appropriate handlers.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, document_store: DocumentStore, llm_config: Union[DeepSeekConfig, OllamaConfig], **kwargs):
        super().__init__(
            name="ProjectManager",
            role=AgentRole.PROJECT_MANAGER,
            description="Coordinates project workflow, manages stakeholder communication, and ensures project objectives are met",
            knowledge_base=knowledge_base,
            document_store=document_store,
            llm_config=llm_config,
            **kwargs
        )
        self.current_project: Optional[ProjectContext] = None
        self.workflow_state = "idle"  # idle, initializing, requirements_gathering, planning, executing
        
        self.logger.info("ProjectManager agent initialized successfully")
        
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa messaggi e coordina il workflow usando analisi intelligente del contenuto"""
        content = message.content
        
        # Skip processing if this is not actual user input
        if not content or content.strip() == "":
            self.logger.debug("Skipping empty message")
            return None
            
        # Skip processing system messages
        #system_phrases = [
        #    "hello, i am the user. i am ready to begin managing a project",
        #    "hello, i am the user. i am ready to begin managing a project.",
        #    "i am ready to begin managing a project",
        #    "ready to begin managing a project"
        #]
        
        #if content.lower().strip() in system_phrases:
        #    self.logger.debug("Skipping system-generated message")
        #    return None
        
        # Additional check: only process meaningful user input
        #meaningful_phrases = ["create", "build", "start", "init", "project", "status", "requirements", "plan", "help"]
        #if not any(phrase in content.lower() for phrase in meaningful_phrases):
        #    self.logger.debug("Skipping non-meaningful message")
        #    return None
        
        # Final check: ensure this is a command or request
        if not content or len(content.strip()) < 5:
            self.logger.debug("Skipping message with insufficient content")
            return None
        
        self.logger.info(f"Processing user command: {content[:100]}...")
        self.logger.debug(f"Processing message: {content[:100]}...")
        
        # Use LLM to analyze user intent and route to appropriate handler
        intent_analysis_prompt = f"""You are a project management assistant. Analyze the user's message and determine their intent.

User message: "{content}"

Based on the agent's capabilities described in its description, classify the user's intent into one of these categories:

1. PROJECT_INITIALIZATION - User wants to start/create a new project
2. STATUS_REQUEST - User wants to know project status or updates
3. REQUIREMENTS_GATHERING - User wants to gather project requirements
4. PROJECT_PLANNING - User wants to create or view project plan
5. SYSTEM_RESTART - User wants to restart or start over
6. GENERAL_COORDINATION - General questions or unclear intent

Consider the context and natural language variations. For example:
- "I want to build an app" = PROJECT_INITIALIZATION
- "How is the project going?" = STATUS_REQUEST
- "Let's plan this out" = PROJECT_PLANNING
- "Start over" = SYSTEM_RESTART

IMPORTANT: Respond with ONLY the category name (e.g., PROJECT_INITIALIZATION). Do not include any other text, explanations, or formatting."""
        
        try:
            intent = await self._call_llm(intent_analysis_prompt)
            intent = intent.strip().upper()
            
            # Clean the response - remove any extra text or formatting
            if intent.startswith("```json"):
                intent = intent[7:]
            elif intent.startswith("```"):
                intent = intent[3:]
            if intent.endswith("```"):
                intent = intent[:-3]
            intent = intent.strip()
            
            # Remove any extra text and keep only the intent
            intent = intent.split('\n')[0].strip()  # Take only the first line
            intent = intent.split('.')[0].strip()   # Remove any trailing period
            
            self.logger.debug(f"Detected user intent: {intent}")
            
            # Route based on detected intent
            if intent == "PROJECT_INITIALIZATION":
                return await self._handle_project_initialization(content)
            elif intent == "STATUS_REQUEST":
                return await self._handle_status_request()
            elif intent == "REQUIREMENTS_GATHERING":
                return await self._coordinate_requirements_gathering()
            elif intent == "PROJECT_PLANNING":
                return await self._coordinate_project_planning()
            elif intent == "SYSTEM_RESTART":
                return await self._restart_project()
            else:
                return await self._handle_general_coordination(content)
                
        except Exception as e:
            self.logger.error(f"Error analyzing user intent: {e}")
            # Fallback to keyword-based intent detection if LLM fails
            return await self._fallback_intent_detection(content)
    
    async def _fallback_intent_detection(self, content: str) -> str:
        """Fallback intent detection using keyword matching when LLM fails."""
        content_lower = content.lower()
        
        self.logger.info("Using fallback keyword-based intent detection")
        
        # Simple keyword-based routing as fallback
        if any(phrase in content_lower for phrase in ["create", "build", "start", "new project", "initialize", "begin"]):
            return await self._handle_project_initialization(content)
        elif any(phrase in content_lower for phrase in ["status", "update", "progress", "how is", "what's happening"]):
            return await self._handle_status_request()
        elif any(phrase in content_lower for phrase in ["requirements", "gather", "collect", "analyze"]):
            return await self._coordinate_requirements_gathering()
        elif any(phrase in content_lower for phrase in ["plan", "planning", "schedule", "timeline"]):
            return await self._coordinate_project_planning()
        elif any(phrase in content_lower for phrase in ["restart", "start over", "new", "reset"]):
            return await self._restart_project()
        else:
            return await self._handle_general_coordination(content)
    
    async def _handle_project_initialization(self, content: str) -> str:
        """Gestisce inizializzazione nuovo progetto con input non strutturato"""
        self.workflow_state = "initializing"
        self.logger.info("Starting project initialization workflow with unstructured input")
        
        # Estrae informazioni dal prompt usando DeepSeek con prompt più intelligente e strutturato
        extraction_prompt = f"""You are a project management expert. Analyze the following user request and extract project information.

User request: {content}

Extract project information and structure it as valid JSON. If information is missing, set those fields to null.
For missing information, provide specific questions to ask the user.

IMPORTANT: Respond with ONLY valid JSON. Do not include any other text, explanations, or markdown formatting.

Expected JSON structure:
{{
    "name": "Project Name or null if unclear",
    "objectives": ["Objective 1", "Objective 2"] or null if unclear,
    "stakeholders": ["Stakeholder 1", "Stakeholder 2"] or null if unclear,
    "constraints": ["Constraint 1", "Constraint 2"] or null if unclear,
    "timeline": "Estimated timeline or null if unclear",
    "budget": "Budget information or null if unclear",
    "missing_info": ["List of specific questions to ask user for missing information"],
    "confidence": "high/medium/low based on how clear the information is"
}}

Be intelligent about extracting information. For example:
- "ecommerce platform" suggests objectives like "online sales", "customer management", "inventory tracking"
- "mobile app" suggests objectives like "mobile user experience", "cross-platform compatibility"
- "AI chatbot" suggests objectives like "automated customer support", "natural language processing"

If the user says something vague like "I want to build something", ask specific clarifying questions.

Remember: Respond with ONLY the JSON object, no other text."""
        
        try:
            # Call LLM to extract project information
            self.logger.debug("Calling LLM for project information extraction...")
            extracted_info = await self._call_llm(extraction_prompt)
            
            self.logger.debug(f"Raw LLM response: {extracted_info[:300]}...")
            
            # Clean the response - remove any markdown formatting or extra text
            extracted_info = extracted_info.strip()
            
            # Handle markdown code blocks
            if extracted_info.startswith("```json"):
                extracted_info = extracted_info[7:]
                self.logger.debug("Removed ```json prefix")
            elif extracted_info.startswith("```"):
                extracted_info = extracted_info[3:]
                self.logger.debug("Removed ``` prefix")
            if extracted_info.endswith("```"):
                extracted_info = extracted_info[:-3]
                self.logger.debug("Removed ``` suffix")
            extracted_info = extracted_info.strip()
            
            self.logger.debug(f"LLM response (cleaned): {extracted_info[:200]}...")
            
            # Try to parse the response as JSON
            import json
            try:
                project_data = json.loads(extracted_info)
                self.logger.info("JSON parsing successful")
            except json.JSONDecodeError as json_error:
                self.logger.error(f"JSON parsing failed: {json_error}")
                self.logger.error(f"Raw LLM response: {extracted_info}")
                
                # Try to extract JSON from the response if it contains other text
                import re
                # Look for JSON object pattern, handling both single and multi-line
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', extracted_info, re.DOTALL)
                if json_match:
                    try:
                        project_data = json.loads(json_match.group())
                        self.logger.info("Successfully extracted JSON from LLM response")
                    except json.JSONDecodeError:
                        # Try a more aggressive extraction
                        try:
                            # Remove any non-JSON text before the first {
                            start_idx = extracted_info.find('{')
                            if start_idx != -1:
                                json_text = extracted_info[start_idx:]
                                project_data = json.loads(json_text)
                                self.logger.info("Successfully extracted JSON using aggressive extraction")
                            else:
                                raise json.JSONDecodeError("No JSON object found", extracted_info, 0)
                        except json.JSONDecodeError:
                            raise json.JSONDecodeError("Failed to parse extracted JSON", extracted_info, 0)
                else:
                    raise json.JSONDecodeError("No JSON found in LLM response", extracted_info, 0)
            
            self.logger.info(f"Project information extracted with confidence: {project_data.get('confidence', 'unknown')}")

            # Check if we have enough information to proceed
            missing_info = project_data.get('missing_info', [])
            confidence = project_data.get('confidence', 'low')
            
            if confidence == 'low' or (missing_info and len(missing_info) > 0):
                # Ask for clarifications
                clarification_questions = "\n".join([f"• {question}" for question in missing_info])
                
                return f"""🤔 **Project Initialization - Need Clarification**

I understand you want to start a new project, but I need some clarification to properly initialize it.

**What I understood so far:**
- **Project Name:** {project_data.get('name', 'Not specified')}
- **Objectives:** {', '.join(project_data.get('objectives', ['Not specified'])) if project_data.get('objectives') else 'Not specified'}
- **Stakeholders:** {', '.join(project_data.get('stakeholders', ['Not specified'])) if project_data.get('stakeholders') else 'Not specified'}
- **Timeline:** {project_data.get('timeline', 'Not specified')}
- **Budget:** {project_data.get('budget', 'Not specified')}

**Please clarify the following:**
{clarification_questions}

**Examples of good responses:**
- "The project name is 'E-commerce Platform' and we need it in 6 months with a budget of $50,000"
- "Our stakeholders are the marketing team and IT department, and we have constraints about using existing infrastructure"
- "The main objective is to increase online sales by 30% within the next quarter"

Please provide the missing information so I can properly initialize your project."""

            # If we have enough information, create the project
            project_name = project_data.get('name', 'New Project')
            if not project_name or project_name == 'null':
                project_name = f"Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create project context
            self.current_project = ProjectContext(
                project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=project_name,
                objectives=project_data.get('objectives', []) if project_data.get('objectives') else ['To be defined'],
                stakeholders=project_data.get('stakeholders', []) if project_data.get('stakeholders') else ['To be defined'],
                constraints=project_data.get('constraints', []) if project_data.get('constraints') else ['To be defined'],
                timeline=project_data.get('timeline', 'TBD'),
                budget=project_data.get('budget', 'TBD')
            )

            # Store in knowledge base
            self.knowledge_base.set_project_context(self.current_project)

            return f"""✅ **Project Initialized Successfully!**

**Project: {self.current_project.name}**
- **Objectives:** {', '.join(self.current_project.objectives)}
- **Stakeholders:** {', '.join(self.current_project.stakeholders)}
- **Constraints:** {', '.join(self.current_project.constraints)}
- **Timeline:** {self.current_project.timeline}
- **Budget:** {self.current_project.budget}

**Next Steps:**
1. 📋 Gather detailed requirements (type 'requirements')
2. 📅 Create project plan (type 'plan project')
3. 👥 Assign resources and team members

**Current Status:** Project initialized and ready for requirements gathering

Type 'requirements' to start the requirements gathering phase, or 'plan project' to create the project plan."""

        except LLMConnectionError as e:
            self.logger.error(f"LLM connection error during project initialization: {e}")
            self.workflow_state = "idle"  # Reset state
            return f"❌ Error connecting to the LLM. Project initialization failed. Please try again later."

        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse LLM response as JSON during project initialization: {e}")
            self.logger.warning(f"Raw LLM response: {extracted_info if 'extracted_info' in locals() else 'No response'}")
            
            # Try simple initialization as fallback
            self.logger.info("Attempting simple project initialization as fallback...")
            try:
                return await self._simple_project_initialization(content)
            except Exception as fallback_error:
                self.logger.error(f"Simple initialization also failed: {fallback_error}")
                self.workflow_state = "idle"  # Reset state
                return f"""❌ **LLM Response Parsing Error**

The AI assistant returned a response that couldn't be parsed. This might be due to:
- Network connectivity issues
- API rate limiting
- Invalid API configuration

**Troubleshooting:**
1. Check your internet connection
2. Verify your API key is valid
3. Try again in a few moments

**Alternative:** You can manually specify project details using this format:
- Project Name: [Your Project Name]
- Objectives: [What you want to achieve]
- Stakeholders: [Who is involved]
- Timeline: [When you need it]
- Budget: [Your budget]"""
                
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during project initialization: {e}", exc_info=True)
            self.workflow_state = "idle"  # Reset state
            return f"❌ An unexpected error occurred during project initialization: {str(e)}"
    
    async def _simple_project_initialization(self, content: str) -> str:
        """Simple project initialization without LLM for basic cases."""
        self.logger.info("Using simple project initialization fallback")
        
        # Extract basic information from content
        content_lower = content.lower()
        
        # Try to extract project name
        project_name = "New Project"
        if "hello world" in content_lower or "python" in content_lower:
            project_name = "Hello World Python Application"
        elif "ecommerce" in content_lower or "e-commerce" in content_lower:
            project_name = "E-commerce Platform"
        elif "mobile app" in content_lower or "app" in content_lower:
            project_name = "Mobile Application"
        elif "website" in content_lower or "web" in content_lower:
            project_name = "Website Project"
        
        # Create basic project context
        self.current_project = ProjectContext(
            project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=project_name,
            objectives=["To be defined based on requirements"],
            stakeholders=["To be identified"],
            constraints=["To be determined"],
            timeline="TBD",
            budget="TBD"
        )

        # Store in knowledge base
        self.knowledge_base.set_project_context(self.current_project)

        return f"""✅ **Project Initialized Successfully!**

**Project: {self.current_project.name}**
- **Objectives:** {', '.join(self.current_project.objectives)}
- **Stakeholders:** {', '.join(self.current_project.stakeholders)}
- **Constraints:** {', '.join(self.current_project.constraints)}
- **Timeline:** {self.current_project.timeline}
- **Budget:** {self.current_project.budget}

**Next Steps:**
1. 📋 Gather detailed requirements (type 'requirements')
2. 📅 Create project plan (type 'plan project')
3. 👥 Assign resources and team members

**Current Status:** Project initialized and ready for requirements gathering

Type 'requirements' to start the requirements gathering phase, or 'plan project' to create the project plan."""
    
    async def _handle_status_request(self) -> str:
        """Handles status and update requests."""
        if not self.current_project:
            return "No active project. Please initialize a project first using 'init_project'."
        
        self.logger.info(f"Status request for project: {self.current_project.name}")
        
        return f"""📊 **Project Status Report**

**Project:** {self.current_project.name}
**Current Phase:** {self.workflow_state.replace('_', ' ').title()}
**Objectives:** {', '.join(self.current_project.objectives)}
**Stakeholders:** {', '.join(self.current_project.stakeholders)}
**Timeline:** {self.current_project.timeline}
**Budget:** {self.current_project.budget}

**Next Actions:**
- Type 'requirements' to gather detailed requirements
- Type 'plan project' to create project plan
- Type 'status' for updates"""
    
    async def _coordinate_requirements_gathering(self) -> str:
        """Coordinates the requirements gathering phase."""
        if not self.current_project:
            return "No active project. Please initialize a project first."
        
        self.workflow_state = "requirements_gathering"
        self.logger.info("Starting requirements gathering phase")
        
        return f"""📋 **Requirements Gathering Phase Started**

**Project:** {self.current_project.name}

I'm now coordinating the requirements gathering process. This involves:
1. Detailed stakeholder interviews
2. Functional requirements analysis
3. Non-functional requirements definition
4. Constraints and assumptions documentation

**Current Status:** Requirements gathering in progress
**Next Phase:** Project planning (after requirements are complete)

Type 'plan project' when requirements are ready, or ask for specific requirements information."""
    
    async def _coordinate_project_planning(self) -> str:
        """Coordinates the project planning phase."""
        if not self.current_project:
            return "No active project. Please initialize a project first."
        
        self.workflow_state = "planning"
        self.logger.info("Starting project planning phase")
        
        return f"""📅 **Project Planning Phase Started**

**Project:** {self.current_project.name}

I'm now coordinating the project planning process. This involves:
1. Work breakdown structure (WBS)
2. Resource allocation
3. Timeline development
4. Risk assessment
5. Communication planning

**Current Status:** Project planning in progress
**Next Phase:** Execution (after plan approval)

The project plan will be created based on the gathered requirements and project context."""
    
    async def _handle_general_coordination(self, content: str) -> str:
        """Handles general messages and provides guidance."""
        if self.workflow_state == "idle":
            return """🚀 **Welcome to Project Management System!**

I can help you manage your projects. Here are some ways to get started:

**Start a new project:**
- "I want to create an e-commerce platform"
- "Initialize a mobile app project for iOS and Android"
- "Start a new project about building an AI chatbot"
- "Create a project for a website redesign"

**Examples of natural language requests:**
- "I need to build a customer management system"
- "We want to develop a mobile game"
- "Create a project for migrating our database to the cloud"
- "I have an idea for a social media app"

Just describe what you want to build or accomplish, and I'll help you get started!"""
        else:
            return f"""📋 **Current Project Status: {self.workflow_state.replace('_', ' ').title()}**

**Available Actions:**
- 📋 Type 'requirements' to gather detailed requirements
- 📅 Type 'plan project' to create project plan  
- 📊 Type 'status' for current project status
- 🔄 Type 'restart' to start a new project

**Current Project:** {self.current_project.name if self.current_project else 'None'}

What would you like to do next?"""

    async def _restart_project(self) -> str:
        """Restarts the project management system with a clean slate."""
        self.workflow_state = "idle"
        self.current_project = None
        self.logger.info("Project management system restarted")
        
        return """🔄 **Project Management System Restarted**

I've cleared the current project and am ready to help you start fresh!

**Start a new project with natural language:**
- "I want to build a mobile app for food delivery"
- "Create a project for a company website redesign"
- "We need to develop an inventory management system"
- "Start a project about building a customer support portal"

Just describe what you want to accomplish, and I'll help you get started!"""
