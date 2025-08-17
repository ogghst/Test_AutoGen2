from typing import Optional, List, Dict, Any
import re
from datetime import datetime
import hashlib
import json

from .base_agent import BaseProjectAgent
from models.data_models import AgentRole, ChangeType, ChangeRecord, DocumentType
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


class ChangeDetectorAgent(BaseProjectAgent):
    """Agente Change Detector - Gestione cambiamenti e change management"""
    
    def __init__(self, knowledge_base: KnowledgeBase, document_store: DocumentStore, **kwargs):
        super().__init__(
            name="ChangeDetector",
            role=AgentRole.CHANGE_DETECTOR,
            description="Monitors project artifacts for changes, tracks modifications, and manages change impact analysis",
            knowledge_base=knowledge_base,
            document_store=document_store,
            **kwargs
        )
        self.change_history: List[ChangeRecord] = []
        self.monitored_artifacts: Dict[str, str] = {}  # artifact_id -> content_hash
        self.change_thresholds = {
            "minor": 0.1,      # 10% change threshold
            "moderate": 0.3,   # 30% change threshold
            "major": 0.5       # 50% change threshold
        }
        
        self.logger.info("ChangeDetector agent initialized successfully")
        
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa messaggi e gestisce change management"""
        content = message.content.lower()
        
        self.logger.debug(f"Processing change detection message: {content[:100]}...")
        
        # Analizza tipo di messaggio
        if "monitor" in content or "track" in content:
            return await self._handle_monitoring_setup(message.content)
        elif "detect" in content or "changes" in content:
            return await self._handle_change_detection()
        elif "analyze" in content and "impact" in content:
            return await self._handle_impact_analysis()
        elif "history" in content or "log" in content:
            return await self._handle_change_history()
        elif "approve" in content or "reject" in content:
            return await self._handle_change_approval(message.content)
        elif "rollback" in content or "revert" in content:
            return await self._handle_change_rollback(message.content)
        else:
            return await self._handle_general_change_management(message.content)
    
    async def _handle_monitoring_setup(self, content: str) -> str:
        """Gestisce la configurazione del monitoring"""
        self.logger.info("Setting up change monitoring")
        
        # Estrae informazioni di monitoring dal messaggio
        extraction_prompt = f"""
        Extract monitoring configuration from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "artifacts": ["artifact1", "artifact2"],
            "monitoring_level": "detailed|summary|critical_only",
            "notification_threshold": "minor|moderate|major",
            "auto_approval": true|false,
            "reviewers": ["reviewer1", "reviewer2"]
        }}
        
        Focus on identifying what should be monitored and how.
        """
        
        try:
            extracted_config = await self._call_deepseek(extraction_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                config_data = json.loads(extracted_config)
                self.logger.info(f"Monitoring configuration extracted: {len(config_data.get('artifacts', []))} artifacts")
                
                # Configura monitoring
                artifacts = config_data.get('artifacts', [])
                for artifact in artifacts:
                    if artifact not in self.monitored_artifacts:
                        # Ottieni hash iniziale
                        initial_hash = self._calculate_content_hash(artifact)
                        self.monitored_artifacts[artifact] = initial_hash
                        self.logger.info(f"Started monitoring artifact: {artifact}")
                
                return f"""✅ Change monitoring setup completed!

**Monitored Artifacts:** {len(self.monitored_artifacts)}
**Monitoring Level:** {config_data.get('monitoring_level', 'detailed')}
**Notification Threshold:** {config_data.get('notification_threshold', 'moderate')}
**Auto Approval:** {config_data.get('auto_approval', False)}

**Next Steps:**
1. Monitor artifacts for changes
2. Detect and analyze changes
3. Assess impact of changes
4. Manage change approval workflow

Type 'detect changes' to check for current changes, or 'analyze impact' to assess recent changes."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse monitoring configuration as JSON")
                return f"""✅ Change monitoring setup started!

I've extracted the following configuration:
{extracted_config}

The monitoring system is being configured. Type 'detect changes' to check for current changes."""
                
        except Exception as e:
            self.logger.error(f"Error during monitoring setup: {e}")
            return f"❌ Error during monitoring setup: {str(e)}"
    
    async def _handle_change_detection(self) -> str:
        """Gestisce la rilevazione dei cambiamenti"""
        if not self.monitored_artifacts:
            return "No artifacts are being monitored. Please set up monitoring first using 'monitor artifacts'."
        
        self.logger.info("Starting change detection process")
        
        detected_changes = []
        
        # Controlla ogni artifact monitorato
        for artifact_id, previous_hash in self.monitored_artifacts.items():
            current_hash = self._calculate_content_hash(artifact_id)
            
            if current_hash != previous_hash:
                # Cambiamento rilevato
                change_record = ChangeRecord(
                    id=f"change_{len(self.change_history) + 1}",
                    artifact_id=artifact_id,
                    change_type=ChangeType.MODIFIED,
                    previous_hash=previous_hash,
                    current_hash=current_hash,
                    detected_at=datetime.now(),
                    status='pending_review',
                    impact_level='unknown'
                )
                
                self.change_history.append(change_record)
                detected_changes.append(change_record)
                
                # Aggiorna hash per prossimo controllo
                self.monitored_artifacts[artifact_id] = current_hash
                
                self.logger.info(f"Change detected in artifact: {artifact_id}")
        
        if detected_changes:
            return f"""🔍 **Change Detection Results**

**Changes Detected:** {len(detected_changes)}

{self._format_changes_summary(detected_changes)}

**Next Steps:**
1. Analyze impact of changes
2. Review change details
3. Approve or reject changes
4. Update change history

Type 'analyze impact' to assess the impact of these changes, or 'change history' to view all changes."""
        else:
            return """✅ **Change Detection Complete**

**Status:** No changes detected

All monitored artifacts are up to date. The system will continue monitoring for changes.

**Next Actions:**
- Type 'analyze impact' to review recent changes
- Type 'change history' to view change log
- Type 'monitor artifacts' to modify monitoring configuration"""
    
    async def _handle_impact_analysis(self) -> str:
        """Gestisce l'analisi dell'impatto dei cambiamenti"""
        if not self.change_history:
            return "No changes to analyze. Please detect changes first using 'detect changes'."
        
        # Filtra cambiamenti recenti (ultime 24 ore)
        recent_changes = [
            change for change in self.change_history 
            if (datetime.now() - change.detected_at).days <= 1
        ]
        
        if not recent_changes:
            return "No recent changes to analyze. All changes are older than 24 hours."
        
        self.logger.info(f"Analyzing impact of {len(recent_changes)} recent changes")
        
        # Analizza impatto usando DeepSeek
        impact_prompt = f"""
        Analyze the impact of the following project changes:
        
        Changes: {[f"{c.artifact_id}: {c.change_type.value}" for c in recent_changes]}
        
        Provide impact analysis covering:
        1. Scope of impact (local, system-wide, cross-system)
        2. Risk assessment (low, medium, high, critical)
        3. Dependencies affected
        4. Timeline implications
        5. Resource requirements
        6. Rollback feasibility
        7. Recommendations for change management
        
        Format as structured markdown with clear impact levels.
        """
        
        try:
            impact_analysis = await self._call_deepseek(impact_prompt)
            
            # Aggiorna livelli di impatto
            for change in recent_changes:
                if 'critical' in impact_analysis.lower():
                    change.impact_level = 'critical'
                elif 'high' in impact_analysis.lower():
                    change.impact_level = 'high'
                elif 'medium' in impact_analysis.lower():
                    change.impact_level = 'medium'
                else:
                    change.impact_level = 'low'
            
            return f"""📊 **Change Impact Analysis Report**

{impact_analysis}

**Recent Changes Summary:**
{self._format_changes_summary(recent_changes)}

**Impact Distribution:**
- Critical: {len([c for c in recent_changes if c.impact_level == 'critical'])}
- High: {len([c for c in recent_changes if c.impact_level == 'high'])}
- Medium: {len([c for c in recent_changes if c.impact_level == 'medium'])}
- Low: {len([c for c in recent_changes if c.impact_level == 'low'])}

**Next Steps:**
1. Review high-impact changes first
2. Plan mitigation strategies
3. Update stakeholders
4. Implement change controls

Type 'change history' to view detailed change log, or 'approve changes' to manage change workflow."""
            
        except Exception as e:
            self.logger.error(f"Error during impact analysis: {e}")
            return f"❌ Error during impact analysis: {str(e)}"
    
    async def _handle_change_history(self) -> str:
        """Gestisce la visualizzazione della cronologia dei cambiamenti"""
        if not self.change_history:
            return "No change history available. No changes have been detected yet."
        
        self.logger.info("Displaying change history")
        
        # Raggruppa cambiamenti per status
        pending_changes = [c for c in self.change_history if c.status == 'pending_review']
        approved_changes = [c for c in self.change_history if c.status == 'approved']
        rejected_changes = [c for c in self.change_history if c.status == 'rejected']
        
        return f"""📋 **Change History Report**

**Total Changes:** {len(self.change_history)}
**Pending Review:** {len(pending_changes)}
**Approved:** {len(approved_changes)}
**Rejected:** {len(rejected_changes)}

**Recent Changes (Last 10):**
{self._format_changes_summary(self.change_history[-10:])}

**Change Status Distribution:**
- 🔄 Pending: {len(pending_changes)}
- ✅ Approved: {len(approved_changes)}
- ❌ Rejected: {len(rejected_changes)}

**Next Actions:**
- Type 'detect changes' to check for new changes
- Type 'analyze impact' to assess recent changes
- Type 'approve changes' to manage approval workflow
- Type 'rollback changes' to revert specific changes

Use specific commands to manage the change workflow."""
    
    async def _handle_change_approval(self, content: str) -> str:
        """Gestisce l'approvazione dei cambiamenti"""
        if not self.change_history:
            return "No changes to approve. Please detect changes first."
        
        pending_changes = [c for c in self.change_history if c.status == 'pending_review']
        if not pending_changes:
            return "No changes pending approval. All changes have been processed."
        
        self.logger.info("Processing change approval workflow")
        
        # Estrae informazioni di approvazione dal messaggio
        approval_prompt = f"""
        Extract change approval information from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "action": "approve|reject",
            "change_ids": ["change_1", "change_2"],
            "reason": "approval or rejection reason",
            "approver": "name of approver",
            "conditions": ["condition1", "condition2"]
        }}
        
        Focus on identifying which changes to approve/reject and why.
        """
        
        try:
            approval_info = await self._call_deepseek(approval_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                approval_data = json.loads(approval_info)
                action = approval_data.get('action', 'approve')
                change_ids = approval_data.get('change_ids', [])
                reason = approval_data.get('reason', 'No reason provided')
                
                # Processa approvazioni/rifiuti
                processed_count = 0
                for change_id in change_ids:
                    change = next((c for c in pending_changes if c.id == change_id), None)
                    if change:
                        change.status = 'approved' if action == 'approve' else 'rejected'
                        change.approved_at = datetime.now() if action == 'approve' else None
                        change.approver = approval_data.get('approver', 'Unknown')
                        change.approval_reason = reason
                        processed_count += 1
                        self.logger.info(f"Change {change_id} {action}d")
                
                return f"""✅ **Change Approval Processed**

**Action:** {action.title()}
**Changes Processed:** {processed_count}/{len(change_ids)}
**Reason:** {reason}
**Approver:** {approval_data.get('approver', 'Unknown')}

**Next Steps:**
1. Review remaining pending changes
2. Monitor approved changes
3. Plan implementation for approved changes
4. Update stakeholders

Type 'change history' to view updated change log, or 'detect changes' to check for new changes."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse approval information as JSON")
                return f"""✅ Change approval process started!

I've extracted the following information:
{approval_info}

The approval workflow is being processed. Type 'change history' to view updated status."""
                
        except Exception as e:
            self.logger.error(f"Error during change approval: {e}")
            return f"❌ Error during change approval: {str(e)}"
    
    async def _handle_change_rollback(self, content: str) -> str:
        """Gestisce il rollback dei cambiamenti"""
        if not self.change_history:
            return "No changes to rollback. Please detect changes first."
        
        approved_changes = [c for c in self.change_history if c.status == 'approved']
        if not approved_changes:
            return "No approved changes to rollback. All changes are pending or rejected."
        
        self.logger.info("Processing change rollback request")
        
        # Estrae informazioni di rollback dal messaggio
        rollback_prompt = f"""
        Extract rollback information from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
        {{
            "change_ids": ["change_1", "change_2"],
            "reason": "rollback reason",
            "requestor": "name of person requesting rollback",
            "target_state": "desired state after rollback"
        }}
        
        Focus on identifying which changes to rollback and why.
        """
        
        try:
            rollback_info = await self._call_deepseek(rollback_prompt)
            
            # Prova a parsare la risposta come JSON
            try:
                rollback_data = json.loads(rollback_info)
                change_ids = rollback_data.get('change_ids', [])
                reason = rollback_data.get('reason', 'No reason provided')
                
                # Processa rollback
                rolled_back_count = 0
                for change_id in change_ids:
                    change = next((c for c in approved_changes if c.id == change_id), None)
                    if change:
                        # Crea record di rollback
                        rollback_record = ChangeRecord(
                            id=f"rollback_{len(self.change_history) + 1}",
                            artifact_id=change.artifact_id,
                            change_type=ChangeType.MODIFIED,
                            previous_hash=change.current_hash,
                            current_hash=change.previous_hash,
                            detected_at=datetime.now(),
                            status='approved',
                            impact_level='high',
                            rollback_of=change.id,
                            rollback_reason=reason
                        )
                        
                        self.change_history.append(rollback_record)
                        rolled_back_count += 1
                        self.logger.info(f"Rollback created for change: {change_id}")
                
                return f"""🔄 **Change Rollback Processed**

**Rollbacks Created:** {rolled_back_count}
**Reason:** {reason}
**Requestor:** {rollback_data.get('requestor', 'Unknown')}

**Next Steps:**
1. Review rollback changes
2. Implement rollback actions
3. Update stakeholders
4. Monitor system stability

Type 'change history' to view updated change log, or 'detect changes' to check current state."""
                
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse rollback information as JSON")
                return f"""✅ Change rollback process started!

I've extracted the following information:
{rollback_info}

The rollback workflow is being processed. Type 'change history' to view updated status."""
                
        except Exception as e:
            self.logger.error(f"Error during change rollback: {e}")
            return f"❌ Error during change rollback: {str(e)}"
    
    async def _handle_general_change_management(self, content: str) -> str:
        """Gestisce messaggi generali sul change management"""
        if not self.monitored_artifacts:
            return """🔍 **Change Detector Ready**

I'm here to help with change management and monitoring. Available commands:

- **'monitor artifacts'** - Set up monitoring for project artifacts
- **'detect changes'** - Check for changes in monitored artifacts
- **'analyze impact'** - Assess impact of recent changes
- **'change history'** - View change log and history
- **'approve changes'** - Manage change approval workflow
- **'rollback changes'** - Create rollback for specific changes

Please start by setting up monitoring for the artifacts you want to track."""
        else:
            return f"""🔍 **Change Management Status**

**Monitored Artifacts:** {len(self.monitored_artifacts)}
**Total Changes Tracked:** {len(self.change_history)}
**Pending Review:** {len([c for c in self.change_history if c.status == 'pending_review'])}

**Available Actions:**
- **'detect changes'** - Check for current changes
- **'analyze impact'** - Assess recent changes
- **'change history'** - View change log
- **'approve changes'** - Manage approvals
- **'rollback changes'** - Handle rollbacks

What would you like to do with change management?"""
    
    def _calculate_content_hash(self, artifact_id: str) -> str:
        """Calcola hash del contenuto di un artifact"""
        try:
            # Per ora restituisce hash basato su ID e timestamp
            # In implementazione reale, leggerebbe il contenuto dell'artifact
            content = f"{artifact_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not calculate hash for artifact {artifact_id}: {e}")
            return "unknown_hash"
    
    def _format_changes_summary(self, changes: List[ChangeRecord]) -> str:
        """Formatta riassunto cambiamenti per output"""
        if not changes:
            return "No changes to display."
        
        summary = []
        for change in changes[-5:]:  # Mostra solo ultimi 5
            status_emoji = {
                'pending_review': '🔄',
                'approved': '✅',
                'rejected': '❌'
            }.get(change.status, '❓')
            
            impact_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(change.impact_level, '⚪')
            
            summary.append(f"{status_emoji} {impact_emoji} **{change.id}** ({change.artifact_id}): {change.change_type.value}")
        
        if len(changes) > 5:
            summary.append(f"... and {len(changes) - 5} more changes")
        
        return "\n".join(summary)
