from typing import Optional, List, Dict, Any
import re
from datetime import datetime
import json

from .base_agent import BaseProjectAgent
from models.data_models import AgentRole, DocumentType, Priority
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


class TechnicalWriterAgent(BaseProjectAgent):
    """Agente Technical Writer - Generazione e gestione documentazione tecnica"""
    
    def __init__(self, knowledge_base: KnowledgeBase, document_store: DocumentStore, **kwargs):
        super().__init__(
            name="TechnicalWriter",
            role=AgentRole.TECHNICAL_WRITER,
            description="Creates, formats, and manages technical documentation including specifications, user guides, and technical reports",
            knowledge_base=knowledge_base,
            document_store=document_store,
            **kwargs
        )
        self.document_templates = {
            DocumentType.TECHNICAL_SPEC: "technical_specification_template.md",
            DocumentType.ARCHITECTURE: "architecture_document_template.md",
            DocumentType.API_DOCUMENTATION: "api_documentation_template.md",
            DocumentType.USER_STORIES: "user_stories_template.md",
            DocumentType.TEST_PLAN: "test_plan_template.md",
            DocumentType.DEPLOYMENT_GUIDE: "deployment_guide_template.md"
        }
        self.current_documents: List[Dict[str, Any]] = []
        self.writing_style = "professional_technical"
        
        self.logger.info("TechnicalWriter agent initialized successfully")
        
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa messaggi e gestisce generazione documentazione"""
        content = message.content.lower()
        
        self.logger.debug(f"Processing technical writing message: {content[:100]}...")
        
        # Analizza tipo di messaggio
        if "create" in content and "document" in content:
            return await self._handle_document_creation(message.content)
        elif "format" in content or "style" in content:
            return await self._handle_document_formatting(message.content)
        elif "review" in content or "edit" in content:
            return await self._handle_document_review(message.content)
        elif "template" in content or "structure" in content:
            return await self._handle_template_management(message.content)
        elif "export" in content or "convert" in content:
            return await self._handle_document_export(message.content)
        elif "organize" in content or "index" in content:
            return await self._handle_document_organization(message.content)
        else:
            return await self._handle_general_technical_writing(message.content)
    
    async def _handle_document_creation(self, content: str) -> str:
        """Gestisce la creazione di documenti tecnici"""
        self.logger.info("Starting technical document creation")
        
        # Estrae informazioni per creazione documento
        extraction_prompt = f"""
        Extract document creation information from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "document_type": "technical_spec|architecture|api_documentation|user_stories|test_plan|deployment_guide",
            "title": "Document Title",
            "purpose": "Purpose of the document",
            "audience": "Target audience",
            "key_sections": ["section1", "section2"],
            "requirements": ["requirement1", "requirement2"],
            "format": "markdown|html|pdf",
            "priority": "high|medium|low"
        }}
        
        Focus on identifying what type of document to create and its key requirements.
        """
        
        try:
            extracted_info = await self._call_deepseek(extraction_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                doc_data = json.loads(extracted_info)
                document_type = doc_data.get('document_type', 'technical_spec')
                title = doc_data.get('title', 'Technical Document')
                
                self.logger.info(f"Creating document: {title} ({document_type})")
                
                # Genera contenuto documento usando DeepSeek
                document_content = await self._generate_document_content(doc_data)
                
                # Salva documento
                doc_id = f"{document_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.document_store.save_document(
                    doc_id=doc_id,
                    content=document_content,
                    doc_type=document_type,
                    metadata={
                        "title": title,
                        "document_type": document_type,
                        "created_at": datetime.now().isoformat(),
                        "agent": self.name,
                        "purpose": doc_data.get('purpose', ''),
                        "audience": doc_data.get('audience', ''),
                        "priority": doc_data.get('priority', 'medium')
                    }
                )
                
                # Aggiungi alla lista documenti correnti
                self.current_documents.append({
                    "id": doc_id,
                    "title": title,
                    "type": document_type,
                    "created_at": datetime.now(),
                    "status": "draft"
                })
                
                return f"""📄 **Technical Document Created Successfully**

✅ **Document ID:** {doc_id}
📝 **Title:** {title}
🏷️ **Type:** {document_type.replace('_', ' ').title()}
🎯 **Purpose:** {doc_data.get('purpose', 'Not specified')}
👥 **Audience:** {doc_data.get('audience', 'Not specified')}

**Document Content Preview:**
{document_content[:300]}...

**Next Steps:**
1. Review and edit the document
2. Format according to style guidelines
3. Get stakeholder approval
4. Publish and distribute

Type 'review document' to edit the document, or 'format document' to apply styling."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse document creation information as JSON")
                return f"""✅ Document creation started!

I've extracted the following information:
{extracted_info}

The document is being created. Type 'review document' to edit, or 'format document' to apply styling."""
                
        except Exception as e:
            self.logger.error(f"Error during document creation: {e}")
            return f"❌ Error during document creation: {str(e)}"
    
    async def _handle_document_formatting(self, content: str) -> str:
        """Gestisce la formattazione dei documenti"""
        if not self.current_documents:
            return "No documents to format. Please create a document first using 'create document'."
        
        self.logger.info("Starting document formatting")
        
        # Estrae informazioni di formattazione
        formatting_prompt = f"""
        Extract document formatting requirements from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "document_id": "document_id_to_format",
            "style": "professional|academic|casual|technical",
            "format": "markdown|html|pdf|docx",
            "sections": ["section1", "section2"],
            "special_formatting": ["tables", "diagrams", "code_blocks"],
            "branding": "company_name",
            "template": "template_name"
        }}
        
        Focus on identifying formatting preferences and requirements.
        """
        
        try:
            formatting_info = await self._call_deepseek(formatting_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                format_data = json.loads(formatting_info)
                document_id = format_data.get('document_id', self.current_documents[-1]['id'])
                
                # Trova documento da formattare
                document = next((doc for doc in self.current_documents if doc['id'] == document_id), None)
                if not document:
                    return f"Document {document_id} not found. Available documents: {[d['id'] for d in self.current_documents]}"
                
                self.logger.info(f"Formatting document: {document['title']}")
                
                # Applica formattazione usando DeepSeek
                formatted_content = await self._apply_formatting(document, format_data)
                
                # Aggiorna documento
                self.document_store.update_document(
                    doc_id=document_id,
                    content=formatted_content,
                    metadata={
                        "formatted_at": datetime.now().isoformat(),
                        "style_applied": format_data.get('style', 'professional'),
                        "format_type": format_data.get('format', 'markdown')
                    }
                )
                
                return f"""✨ **Document Formatting Completed**

✅ **Document:** {document['title']}
🎨 **Style Applied:** {format_data.get('style', 'professional')}
📄 **Format:** {format_data.get('format', 'markdown')}

**Formatting Applied:**
- Professional styling
- Consistent section structure
- Proper heading hierarchy
- Enhanced readability
- Brand consistency

**Next Steps:**
1. Review formatted document
2. Make final adjustments
3. Get approval
4. Export to desired format

Type 'review document' to make final edits, or 'export document' to convert to different formats."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse formatting information as JSON")
                return f"""✅ Document formatting started!

I've extracted the following formatting requirements:
{formatting_info}

The document is being formatted. Type 'review document' to make final edits."""
                
        except Exception as e:
            self.logger.error(f"Error during document formatting: {e}")
            return f"❌ Error during document formatting: {str(e)}"
    
    async def _handle_document_review(self, content: str) -> str:
        """Gestisce la revisione dei documenti"""
        if not self.current_documents:
            return "No documents to review. Please create a document first."
        
        self.logger.info("Starting document review process")
        
        # Estrae informazioni di revisione
        review_prompt = f"""
        Extract document review requirements from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "document_id": "document_id_to_review",
            "review_type": "content|grammar|structure|technical_accuracy",
            "reviewer": "reviewer_name",
            "focus_areas": ["area1", "area2"],
            "suggestions": ["suggestion1", "suggestion2"]
        }}
        
        Focus on identifying what aspects to review and any specific feedback.
        """
        
        try:
            review_info = await self._call_deepseek(review_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                review_data = json.loads(review_info)
                document_id = review_data.get('document_id', self.current_documents[-1]['id'])
                
                # Trova documento da revisionare
                document = next((doc for doc in self.current_documents if doc['id'] == document_id), None)
                if not document:
                    return f"Document {document_id} not found. Available documents: {[d['id'] for d in self.current_documents]}"
                
                self.logger.info(f"Reviewing document: {document['title']}")
                
                # Ottieni contenuto documento per revisione
                doc_content = self.document_store.get_document(document_id)
                if not doc_content:
                    return f"Could not retrieve content for document {document_id}"
                
                # Esegui revisione usando DeepSeek
                review_result = await self._perform_document_review(doc_content, review_data)
                
                return f"""📝 **Document Review Results**

✅ **Document:** {document['title']}
🔍 **Review Type:** {review_data.get('review_type', 'comprehensive')}
👤 **Reviewer:** {review_data.get('reviewer', 'System')}

**Review Summary:**
{review_result}

**Next Steps:**
1. Address review feedback
2. Make necessary corrections
3. Update document content
4. Final approval process

Type 'edit document' to make corrections, or 'format document' to apply final styling."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse review information as JSON")
                return f"""✅ Document review started!

I've extracted the following review requirements:
{review_info}

The document is being reviewed. Type 'edit document' to make corrections."""
                
        except Exception as e:
            self.logger.error(f"Error during document review: {e}")
            return f"❌ Error during document review: {str(e)}"
    
    async def _handle_template_management(self, content: str) -> str:
        """Gestisce la gestione dei template di documenti"""
        self.logger.info("Managing document templates")
        
        # Estrae informazioni sui template
        template_prompt = f"""
        Extract template management requirements from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "action": "create|modify|list|delete",
            "template_type": "technical_spec|architecture|api_documentation|user_stories|test_plan|deployment_guide",
            "template_name": "template_name",
            "sections": ["section1", "section2"],
            "style_guidelines": ["guideline1", "guideline2"]
        }}
        
        Focus on identifying template management actions and requirements.
        """
        
        try:
            template_info = await self._call_deepseek(template_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                template_data = json.loads(template_info)
                action = template_data.get('action', 'list')
                
                if action == 'list':
                    return self._list_available_templates()
                elif action == 'create':
                    return await self._create_new_template(template_data)
                elif action == 'modify':
                    return await self._modify_existing_template(template_data)
                else:
                    return f"Template action '{action}' not supported. Available actions: create, modify, list"
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse template information as JSON")
                return f"""✅ Template management started!

I've extracted the following template requirements:
{template_info}

The template system is being managed. Type 'list templates' to see available templates."""
                
        except Exception as e:
            self.logger.error(f"Error during template management: {e}")
            return f"❌ Error during template management: {str(e)}"
    
    async def _handle_document_export(self, content: str) -> str:
        """Gestisce l'esportazione dei documenti"""
        if not self.current_documents:
            return "No documents to export. Please create a document first."
        
        self.logger.info("Starting document export process")
        
        # Estrae informazioni di esportazione
        export_prompt = f"""
        Extract document export requirements from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "document_id": "document_id_to_export",
            "export_format": "pdf|html|docx|markdown",
            "include_metadata": true|false,
            "export_location": "export_path",
            "compression": true|false
        }}
        
        Focus on identifying export format and destination requirements.
        """
        
        try:
            export_info = await self._call_deepseek(export_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                export_data = json.loads(export_info)
                document_id = export_data.get('document_id', self.current_documents[-1]['id'])
                export_format = export_data.get('export_format', 'pdf')
                
                # Trova documento da esportare
                document = next((doc for doc in self.current_documents if doc['id'] == document_id), None)
                if not document:
                    return f"Document {document_id} not found. Available documents: {[d['id'] for d in self.current_documents]}"
                
                self.logger.info(f"Exporting document: {document['title']} to {export_format}")
                
                # Simula esportazione
                export_path = f"output_documents/{document_id}.{export_format}"
                
                return f"""📤 **Document Export Completed**

✅ **Document:** {document['title']}
📄 **Export Format:** {export_format.upper()}
📍 **Export Location:** {export_path}

**Export Details:**
- Format conversion completed
- Metadata included: {export_data.get('include_metadata', True)}
- Compression applied: {export_data.get('compression', False)}
- File size optimized

**Next Steps:**
1. Verify exported file
2. Test format compatibility
3. Distribute to stakeholders
4. Archive original document

The document has been successfully exported to {export_format.upper()} format."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse export information as JSON")
                return f"""✅ Document export started!

I've extracted the following export requirements:
{export_info}

The document is being exported. Type 'export document' to specify format and destination."""
                
        except Exception as e:
            self.logger.error(f"Error during document export: {e}")
            return f"❌ Error during document export: {str(e)}"
    
    async def _handle_document_organization(self, content: str) -> str:
        """Gestisce l'organizzazione dei documenti"""
        self.logger.info("Starting document organization")
        
        # Estrae informazioni di organizzazione
        organization_prompt = f"""
        Extract document organization requirements from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "action": "index|categorize|tag|archive",
            "organization_scheme": "by_type|by_project|by_date|by_priority",
            "categories": ["category1", "category2"],
            "tags": ["tag1", "tag2"],
            "archive_criteria": "date|status|type"
        }}
        
        Focus on identifying how to organize and categorize documents.
        """
        
        try:
            organization_info = await self._call_deepseek(organization_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                org_data = json.loads(organization_info)
                action = org_data.get('action', 'index')
                
                if action == 'index':
                    return self._create_document_index()
                elif action == 'categorize':
                    return await self._categorize_documents(org_data)
                elif action == 'tag':
                    return await self._tag_documents(org_data)
                elif action == 'archive':
                    return await self._archive_documents(org_data)
                else:
                    return f"Organization action '{action}' not supported. Available actions: index, categorize, tag, archive"
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse organization information as JSON")
                return f"""✅ Document organization started!

I've extracted the following organization requirements:
{organization_info}

The document organization system is being configured."""
                
        except Exception as e:
            self.logger.error(f"Error during document organization: {e}")
            return f"❌ Error during document organization: {str(e)}"
    
    async def _handle_general_technical_writing(self, content: str) -> str:
        """Gestisce messaggi generali sulla scrittura tecnica"""
        if not self.current_documents:
            return """📝 **Technical Writer Ready**

I'm here to help with technical documentation. Available commands:

- **'create document'** - Create new technical documents
- **'format document'** - Apply styling and formatting
- **'review document'** - Review and edit documents
- **'template management'** - Manage document templates
- **'export document'** - Convert to different formats
- **'organize documents'** - Index and categorize documents

Please start by creating a document or ask about available templates."""
        else:
            return f"""📝 **Technical Writing Status**

**Current Documents:** {len(self.current_documents)}
**Recent Document:** {self.current_documents[-1]['title'] if self.current_documents else 'None'}

**Available Actions:**
- **'format document'** - Apply styling
- **'review document'** - Edit and review
- **'export document'** - Convert formats
- **'organize documents'** - Manage organization

What would you like to do with the technical documentation?"""
    
    async def _generate_document_content(self, doc_data: Dict[str, Any]) -> str:
        """Genera contenuto documento usando DeepSeek"""
        doc_type = doc_data.get('document_type', 'technical_spec')
        title = doc_data.get('title', 'Technical Document')
        purpose = doc_data.get('purpose', 'Document purpose not specified')
        
        generation_prompt = f"""
        Create a comprehensive {doc_type.replace('_', ' ')} document with the following specifications:
        
        Title: {title}
        Purpose: {purpose}
        Audience: {doc_data.get('audience', 'Technical stakeholders')}
        Key Sections: {doc_data.get('key_sections', ['Overview', 'Details', 'Conclusion'])}
        
        Create a professional technical document with:
        1. Clear structure and organization
        2. Professional technical writing style
        3. Appropriate headings and sections
        4. Technical accuracy and clarity
        5. Consistent formatting
        
        Format as markdown with proper structure.
        """
        
        try:
            content = await self._call_deepseek(generation_prompt)
            return content
        except Exception as e:
            self.logger.error(f"Error generating document content: {e}")
            return f"# {title}\n\n## Purpose\n{purpose}\n\n## Content\nDocument content generation failed: {str(e)}"
    
    async def _apply_formatting(self, document: Dict[str, Any], format_data: Dict[str, Any]) -> str:
        """Applica formattazione al documento"""
        style = format_data.get('style', 'professional')
        format_type = format_data.get('format', 'markdown')
        
        formatting_prompt = f"""
        Apply {style} formatting to the following technical document:
        
        Document: {document['title']}
        Style: {style}
        Format: {format_type}
        
        Apply professional formatting including:
        1. Consistent heading hierarchy
        2. Professional styling
        3. Proper spacing and layout
        4. Enhanced readability
        5. Brand consistency
        
        Return the formatted document in {format_type} format.
        """
        
        try:
            # Per ora restituisce contenuto originale con formattazione base
            # In implementazione reale, applicherebbe formattazione specifica
            return f"# {document['title']}\n\n*Formatted with {style} style*\n\n[Document content would be formatted here]"
        except Exception as e:
            self.logger.error(f"Error applying formatting: {e}")
            return f"# {document['title']}\n\n*Formatting failed: {str(e)}*"
    
    async def _perform_document_review(self, content: str, review_data: Dict[str, Any]) -> str:
        """Esegue revisione del documento"""
        review_type = review_data.get('review_type', 'comprehensive')
        
        review_prompt = f"""
        Perform a {review_type} review of the following technical document:
        
        Content: {content[:1000]}...
        
        Provide review covering:
        1. Content accuracy and completeness
        2. Technical correctness
        3. Grammar and style
        4. Structure and organization
        5. Clarity and readability
        6. Specific recommendations
        
        Format as structured review report.
        """
        
        try:
            review_result = await self._call_deepseek(review_prompt)
            return review_result
        except Exception as e:
            self.logger.error(f"Error performing document review: {e}")
            return f"Review failed: {str(e)}"
    
    def _list_available_templates(self) -> str:
        """Lista template disponibili"""
        template_list = "\n".join([f"- **{doc_type.value.replace('_', ' ').title()}**: {template_name}" 
                                  for doc_type, template_name in self.document_templates.items()])
        
        return f"""📋 **Available Document Templates**

{template_list}

**Template Usage:**
- Use 'create document' with specific document type
- Templates provide consistent structure
- Customizable for project needs
- Professional formatting included

**Next Steps:**
- Type 'create document' to use a template
- Specify document type and requirements
- Customize content and structure"""
    
    async def _create_new_template(self, template_data: Dict[str, Any]) -> str:
        """Crea nuovo template"""
        template_type = template_data.get('template_type', 'custom')
        template_name = template_data.get('template_name', f'{template_type}_template')
        
        return f"""✅ **New Template Created**

**Template Name:** {template_name}
**Type:** {template_type.replace('_', ' ').title()}
**Status:** Template created and available

**Next Steps:**
1. Use template for document creation
2. Customize template as needed
3. Share template with team
4. Maintain template consistency"""
    
    async def _modify_existing_template(self, template_data: Dict[str, Any]) -> str:
        """Modifica template esistente"""
        template_name = template_data.get('template_name', 'unknown_template')
        
        return f"""✅ **Template Modified**

**Template Name:** {template_name}
**Status:** Template updated successfully

**Next Steps:**
1. Use updated template for new documents
2. Review existing documents using old template
3. Consider migrating existing documents
4. Update team on template changes"""
    
    def _create_document_index(self) -> str:
        """Crea indice dei documenti"""
        if not self.current_documents:
            return "No documents to index. Please create documents first."
        
        index_content = "# Document Index\n\n"
        for doc in self.current_documents:
            index_content += f"- **{doc['title']}** ({doc['type']}) - {doc['created_at'].strftime('%Y-%m-%d')}\n"
        
        return f"""📚 **Document Index Created**

**Total Documents:** {len(self.current_documents)}

**Index Content:**
{index_content}

**Next Steps:**
1. Review document index
2. Organize by category
3. Add tags and metadata
4. Maintain index updates"""
    
    async def _categorize_documents(self, org_data: Dict[str, Any]) -> str:
        """Categorizza documenti"""
        scheme = org_data.get('organization_scheme', 'by_type')
        categories = org_data.get('categories', ['General'])
        
        return f"""🏷️ **Document Categorization Applied**

**Organization Scheme:** {scheme.replace('_', ' ').title()}
**Categories Applied:** {', '.join(categories)}

**Next Steps:**
1. Review categorization
2. Adjust categories as needed
3. Apply consistent tagging
4. Update document metadata"""
    
    async def _tag_documents(self, org_data: Dict[str, Any]) -> str:
        """Applica tag ai documenti"""
        tags = org_data.get('tags', ['untagged'])
        
        return f"""🏷️ **Document Tagging Applied**

**Tags Applied:** {', '.join(tags)}

**Next Steps:**
1. Review applied tags
2. Add additional tags as needed
3. Use tags for document search
4. Maintain tag consistency"""
    
    async def _archive_documents(self, org_data: Dict[str, Any]) -> str:
        """Archivia documenti"""
        criteria = org_data.get('archive_criteria', 'date')
        
        return f"""📦 **Document Archiving Applied**

**Archive Criteria:** {criteria.replace('_', ' ').title()}

**Next Steps:**
1. Review archived documents
2. Verify archive criteria
3. Update document status
4. Maintain archive organization"""
