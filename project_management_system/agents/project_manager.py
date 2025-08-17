from typing import Optional, List, Dict, Any
import re
from datetime import datetime

from .base_agent import BaseProjectAgent, DeepSeekConfig, OllamaConfig
from typing import Union
from models.data_models import AgentConfig, DeepSeekConfig, OllamaConfig, AgentRole
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


class ProjectManagerAgent(BaseProjectAgent):
    """Agente Project Manager - Orchestratore principale"""
    
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
        """Processa messaggi e coordina il workflow"""
        content = message.content.lower()
        
        self.logger.debug(f"Processing message: {content[:100]}...")
        
        # Analizza tipo di messaggio
        if "init_project" in content or "start project" in content:
            return await self._handle_project_initialization(message.content)
        elif "status" in content or "update" in content:
            return await self._handle_status_request()
        elif "requirements" in content and self.workflow_state == "initializing":
            return await self._coordinate_requirements_gathering()
        elif "plan" in content and "project" in content:
            return await self._coordinate_project_planning()
        else:
            return await self._handle_general_coordination(message.content)
    
    async def _handle_project_initialization(self, content: str) -> str:
        """Gestisce inizializzazione nuovo progetto"""
        self.workflow_state = "initializing"
        self.logger.info("Starting project initialization workflow")
        
        # Estrae informazioni dal prompt usando DeepSeek
        extraction_prompt = f"""
        Extract project information from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "name": "Project Name",
            "objectives": ["Objective 1", "Objective 2"],
            "stakeholders": ["Stakeholder 1", "Stakeholder 2"],
            "constraints": ["Constraint 1", "Constraint 2"],
            "timeline": "Estimated timeline",
            "budget": "Budget information"
        }}
        """
        
        try:
            # Call DeepSeek to extract project information
            extracted_info = await self._call_llm(extraction_prompt)
            
            # Try to parse the response as JSON
            import json
            try:
                project_data = json.loads(extracted_info)
                self.logger.info(f"Project information extracted: {project_data.get('name', 'Unknown')}")
                
                # Create project context
                self.current_project = ProjectContext(
                    project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    name=project_data.get('name', 'New Project'),
                    objectives=project_data.get('objectives', []),
                    stakeholders=project_data.get('stakeholders', []),
                    constraints=project_data.get('constraints', []),
                    timeline=project_data.get('timeline', 'TBD'),
                    budget=project_data.get('budget', 'TBD')
                )
                
                # Store in knowledge base
                self.knowledge_base.set_project_context(self.current_project)
                
                return f"""✅ Project initialized successfully!

**Project: {self.current_project.name}**
- **Objectives:** {', '.join(self.current_project.objectives)}
- **Stakeholders:** {', '.join(self.current_project.stakeholders)}
- **Constraints:** {', '.join(self.current_project.constraints)}
- **Timeline:** {self.current_project.timeline}
- **Budget:** {self.current_project.budget}

Next steps:
1. Gather detailed requirements
2. Create project plan
3. Assign resources

Type 'requirements' to start requirements gathering, or 'plan project' to create the project plan."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse extracted project information as JSON")
                return f"""✅ Project initialization started!

I've extracted the following information:
{extracted_info}

The project is now in initialization phase. Type 'requirements' to start gathering detailed requirements, or 'plan project' to create the project plan."""
                
        except Exception as e:
            self.logger.error(f"Error during project initialization: {e}")
            return f"❌ Error during project initialization: {str(e)}"
    
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
        
        if self.workflow_state == "idle":
            return "Project not initialized. Please start by initializing a project."
        
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
            return "Project not initialized. Please start by initializing a project. For example: 'init_project Name: E-commerce Platform'"
        else:
            return f"Received general message. Current project status: {self.workflow_state}. What would you like to do next?"
