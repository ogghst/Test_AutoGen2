from typing import Optional, List, Dict, Any
import re
from datetime import datetime

from .base_agent import BaseProjectAgent
from models.data_models import AgentRole, Requirement, RequirementType, Priority
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


class RequirementsAnalystAgent(BaseProjectAgent):
    """Agente Requirements Analyst - Raccolta e analisi requisiti"""
    
    def __init__(self, knowledge_base: KnowledgeBase, document_store: DocumentStore, **kwargs):
        super().__init__(
            name="RequirementsAnalyst",
            role=AgentRole.REQUIREMENTS_ANALYST,
            description="Analyzes stakeholder needs, gathers functional and non-functional requirements, and creates comprehensive requirements documentation",
            knowledge_base=knowledge_base,
            document_store=document_store,
            **kwargs
        )
        self.current_requirements: List[Requirement] = []
        self.interview_questions = [
            "What is the primary goal of this project?",
            "Who are the end users and what are their needs?",
            "What are the key features that must be included?",
            "What are the performance requirements?",
            "What are the security and compliance requirements?",
            "What are the integration requirements with existing systems?",
            "What are the constraints (time, budget, technology)?"
        ]
        
        self.logger.info("RequirementsAnalyst agent initialized successfully")
        
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa messaggi e gestisce raccolta requisiti"""
        content = message.content.lower()
        
        self.logger.debug(f"Processing requirements message: {content[:100]}...")
        
        # Analizza tipo di messaggio
        if "gather" in content or "collect" in content or "requirements" in content:
            return await self._handle_requirements_gathering(message.content)
        elif "analyze" in content or "review" in content:
            return await self._handle_requirements_analysis()
        elif "document" in content or "create" in content:
            return await self._handle_requirements_documentation()
        elif "interview" in content or "questions" in content:
            return await self._handle_interview_questions()
        elif "validate" in content or "verify" in content:
            return await self._handle_requirements_validation()
        else:
            return await self._handle_general_requirements(message.content)
    
    async def _handle_requirements_gathering(self, content: str) -> str:
        """Gestisce la raccolta di requisiti"""
        self.logger.info("Starting requirements gathering process")
        
        # Estrae requisiti dal messaggio usando DeepSeek
        extraction_prompt = f"""
        Analyze the following text and extract project requirements. Structure the response as a JSON array of requirements:
        
        Text: {content}
        
        For each requirement, include:
        {{
            "id": "unique_requirement_id",
            "type": "functional|non_functional|business|technical",
            "description": "clear description of the requirement",
            "priority": "high|medium|low|critical",
            "source": "stakeholder or source of the requirement",
            "acceptance_criteria": ["criterion 1", "criterion 2"],
            "dependencies": ["dependency 1", "dependency 2"]
        }}
        
        Focus on extracting actionable, specific requirements.
        """
        
        try:
            extracted_requirements = await self._call_llm(extraction_prompt)
            
            # Prova a parsare la risposta come JSON
            import json
            try:
                requirements_data = json.loads(extracted_requirements)
                self.logger.info(f"Extracted {len(requirements_data)} requirements")
                
                # Crea oggetti Requirement
                for req_data in requirements_data:
                    requirement = Requirement(
                        id=req_data.get('id', f"req_{len(self.current_requirements) + 1}"),
                        type=RequirementType(req_data.get('type', 'functional')),
                        description=req_data.get('description', ''),
                        priority=Priority(req_data.get('priority', 'medium')),
                        source=req_data.get('source', 'Unknown'),
                        acceptance_criteria=req_data.get('acceptance_criteria', []),
                        dependencies=req_data.get('dependencies', []),
                        created_at=datetime.now(),
                        status='draft'
                    )
                    self.current_requirements.append(requirement)
                
                return f"""✅ Requirements gathered successfully!

**Extracted Requirements:**
{self._format_requirements_summary()}

**Next Steps:**
1. Review and validate requirements
2. Document requirements formally
3. Create user stories (if using Agile)
4. Define acceptance criteria

Type 'analyze requirements' to review the gathered requirements, or 'document requirements' to create formal documentation."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse extracted requirements as JSON")
                return f"""✅ Requirements gathering started!

I've extracted the following information:
{extracted_requirements}

The requirements are being processed. Type 'analyze requirements' to review what we have, or 'document requirements' to create formal documentation."""
                
        except Exception as e:
            self.logger.error(f"Error during requirements gathering: {e}")
            return f"❌ Error during requirements gathering: {str(e)}"
    
    async def _handle_requirements_analysis(self) -> str:
        """Gestisce l'analisi dei requisiti"""
        if not self.current_requirements:
            return "No requirements to analyze. Please gather requirements first using 'gather requirements'."
        
        self.logger.info("Starting requirements analysis")
        
        # Analizza requisiti usando DeepSeek
        analysis_prompt = f"""
        Analyze the following requirements and provide insights:
        
        Requirements: {[req.description for req in self.current_requirements]}
        
        Provide analysis covering:
        1. Completeness assessment
        2. Priority distribution
        3. Dependencies identification
        4. Potential conflicts
        5. Missing requirements
        6. Recommendations for improvement
        
        Format as structured markdown.
        """
        
        try:
            analysis_result = await self._call_llm(analysis_prompt)
            
            return f"""📊 **Requirements Analysis Report**

{analysis_result}

**Requirements Summary:**
{self._format_requirements_summary()}

**Next Steps:**
1. Address identified gaps
2. Resolve conflicts
3. Document requirements formally
4. Create user stories (if Agile)

Type 'document requirements' to create formal documentation."""
            
        except Exception as e:
            self.logger.error(f"Error during requirements analysis: {e}")
            return f"❌ Error during requirements analysis: {str(e)}"
    
    async def _handle_requirements_documentation(self) -> str:
        """Gestisce la documentazione dei requisiti"""
        if not self.current_requirements:
            return "No requirements to document. Please gather requirements first."
        
        self.logger.info("Creating requirements documentation")
        
        # Genera documentazione usando DeepSeek
        doc_prompt = f"""
        Create comprehensive requirements documentation for the following requirements:
        
        Requirements: {[req.description for req in self.current_requirements]}
        
        Create a professional requirements document including:
        1. Executive Summary
        2. Project Overview
        3. Functional Requirements
        4. Non-Functional Requirements
        5. User Stories (if applicable)
        6. Acceptance Criteria
        7. Dependencies and Constraints
        8. Assumptions and Risks
        
        Format as professional markdown with clear structure.
        """
        
        try:
            documentation = await self._call_llm(doc_prompt)
            
            # Salva documentazione
            doc_id = f"requirements_doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.document_store.save_document(
                doc_id=doc_id,
                content=documentation,
                doc_type="requirements",
                metadata={
                    "requirements_count": len(self.current_requirements),
                    "created_at": datetime.now().isoformat(),
                    "agent": self.name
                }
            )
            
            return f"""📄 **Requirements Documentation Created**

✅ Document saved with ID: {doc_id}

**Document Content:**
{documentation[:500]}...

**Next Steps:**
1. Review documentation with stakeholders
2. Get approval and sign-off
3. Use as input for project planning
4. Track changes and updates

The requirements document is now ready for stakeholder review and project planning."""
            
        except Exception as e:
            self.logger.error(f"Error during requirements documentation: {e}")
            return f"❌ Error during requirements documentation: {str(e)}"
    
    async def _handle_interview_questions(self) -> str:
        """Gestisce domande di intervista per raccolta requisiti"""
        self.logger.info("Providing interview questions for requirements gathering")
        
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.interview_questions)])
        
        return f"""🎯 **Requirements Gathering Interview Questions**

Use these questions to gather comprehensive requirements from stakeholders:

{questions_text}

**Additional Tips:**
- Ask follow-up questions based on responses
- Document all answers thoroughly
- Identify conflicting requirements early
- Clarify ambiguous statements
- Get specific examples and use cases

**Next Steps:**
1. Conduct stakeholder interviews
2. Document responses
3. Use 'gather requirements' to process the information
4. Analyze and validate requirements

Type 'gather requirements' when you have interview responses to process."""
    
    async def _handle_requirements_validation(self) -> str:
        """Gestisce la validazione dei requisiti"""
        if not self.current_requirements:
            return "No requirements to validate. Please gather requirements first."
        
        self.logger.info("Starting requirements validation")
        
        # Valida requisiti usando DeepSeek
        validation_prompt = f"""
        Validate the following requirements for clarity, completeness, and feasibility:
        
        Requirements: {[req.description for req in self.current_requirements]}
        
        Provide validation covering:
        1. Clarity assessment (are requirements clear and unambiguous?)
        2. Completeness check (are all necessary requirements included?)
        3. Feasibility analysis (are requirements technically and economically feasible?)
        4. Testability evaluation (can requirements be tested?)
        5. Consistency check (are requirements consistent with each other?)
        6. Specific recommendations for improvement
        
        Format as structured markdown with clear validation results.
        """
        
        try:
            validation_result = await self._call_llm(validation_prompt)
            
            return f"""✅ **Requirements Validation Report**

{validation_result}

**Validation Summary:**
- Total Requirements: {len(self.current_requirements)}
- High Priority: {len([r for r in self.current_requirements if r.priority == Priority.HIGH])}
- Medium Priority: {len([r for r in self.current_requirements if r.priority == Priority.MEDIUM])}
- Low Priority: {len([r for r in self.current_requirements if r.priority == Priority.LOW])}

**Next Steps:**
1. Address validation issues
2. Refine unclear requirements
3. Add missing requirements
4. Finalize documentation

Type 'document requirements' to create the final requirements document."""
            
        except Exception as e:
            self.logger.error(f"Error during requirements validation: {e}")
            return f"❌ Error during requirements validation: {str(e)}"
    
    async def _handle_general_requirements(self, content: str) -> str:
        """Gestisce messaggi generali sui requisiti"""
        if not self.current_requirements:
            return """📋 **Requirements Analyst Ready**

I'm here to help with requirements gathering and analysis. Available commands:

- **'gather requirements'** - Extract requirements from text
- **'analyze requirements'** - Review and analyze gathered requirements  
- **'document requirements'** - Create formal requirements documentation
- **'interview questions'** - Get questions for stakeholder interviews
- **'validate requirements'** - Validate requirements quality

Please start by gathering requirements or ask for interview questions."""
        else:
            return f"""📋 **Requirements Status**

**Current Requirements:** {len(self.current_requirements)} gathered

**Available Actions:**
- **'analyze requirements'** - Review what we have
- **'document requirements'** - Create formal documentation
- **'validate requirements'** - Quality check
- **'gather requirements'** - Add more requirements

What would you like to do next with the requirements?"""
    
    def _format_requirements_summary(self) -> str:
        """Formatta riassunto requisiti per output"""
        if not self.current_requirements:
            return "No requirements gathered yet."
        
        summary = []
        for req in self.current_requirements:
            priority_emoji = {
                Priority.CRITICAL: "🔴",
                Priority.HIGH: "🟠", 
                Priority.MEDIUM: "🟡",
                Priority.LOW: "🟢"
            }.get(req.priority, "⚪")
            
            summary.append(f"{priority_emoji} **{req.id}** ({req.type.value}): {req.description[:100]}...")
        
        return "\n".join(summary)
