"""
Document Store per il sistema multi-agente
Gestisce persistenza, versioning e retrieval dei documenti generati
Compatible with AutoGen 0.7.2+ AgentChat API
"""

import asyncio
import hashlib
import json
import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Sequence, Callable, AsyncGenerator
import threading
from dataclasses import asdict
from copy import deepcopy

# AutoGen 0.7.2+ compatibility imports
try:
    from autogen_agentchat.messages import BaseChatMessage, TextMessage
    from autogen_agentchat.base import Response, TaskResult
    from autogen_core import CancellationToken
    from autogen_core.memory import Memory, MemoryContent
    AUTOGEN_AVAILABLE = True
except ImportError:
    # Fallback per development senza AutoGen
    BaseChatMessage = Any
    TextMessage = Any
    Response = Any
    TaskResult = Any
    CancellationToken = Any
    Memory = Any
    MemoryContent = Any
    AUTOGEN_AVAILABLE = False

from models.data_models import (
    Document, DocumentType, ChangeEvent, ChangeType, 
    serialize_datetime, deserialize_datetime, validate_document,
    ValidationError, generate_uuid
)
from config.logging_config import get_logger


# ============================================================================
# LOGGER SETUP
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class DocumentStoreError(Exception):
    """Eccezione base per errori del document store"""
    pass


class DocumentNotFoundError(DocumentStoreError):
    """Documento non trovato"""
    pass


class DocumentVersionConflictError(DocumentStoreError):
    """Conflitto di versione documento"""
    pass


class StorageError(DocumentStoreError):
    """Errore di storage/filesystem"""
    pass


class IndexCorruptedError(DocumentStoreError):
    """Indice documenti corrotto"""
    pass


# ============================================================================
# DOCUMENT STORE CORE
# ============================================================================

class DocumentStore:
    """Store per documenti di output generati dagli agenti"""
    
    def __init__(self,
                 storage_path: str = "documents",
                 enable_versioning: bool = False,
                 enable_backup: bool = False,
                 enable_search_index: bool = False,
                 auto_cleanup_versions: bool = False,
                 max_versions_per_document: int = 10,
                 max_concurrent_operations: int = 10):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.documents_path = self.storage_path / "content"
        self.versions_path = self.storage_path / "versions"
        self.backup_path = self.storage_path / "backups"
        self.index_file = self.storage_path / "document_index.json"
        self.search_index_file = self.storage_path / "search_index.json"

        self.documents_path.mkdir(exist_ok=True)

        self.documents: Dict[str, Document] = {}
        self.search_index: Dict[str, List[str]] = {}
        self._change_callbacks: List[Callable] = []
        self._memory_store = None

        self.enable_versioning = enable_versioning
        self.enable_backup = enable_backup
        self.enable_search_index = enable_search_index
        self.auto_cleanup_versions = auto_cleanup_versions
        self.max_versions_per_document = max_versions_per_document

        if self.enable_versioning:
            self.versions_path.mkdir(exist_ok=True)
        if self.enable_backup:
            self.backup_path.mkdir(exist_ok=True)

        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_operations)
        self._lock = threading.Lock()
        self.logger = get_logger(__name__)

        self._load_index()
        if self.enable_search_index:
            self._load_search_index()

        self.logger.info(f"DocumentStore initialized with storage path: {self.storage_path}")

    def _load_search_index(self):
        """Carica l'indice di ricerca da file"""
        if not self.search_index_file.exists():
            self.search_index = {}
            return
        try:
            with open(self.search_index_file, 'r', encoding='utf-8') as f:
                self.search_index = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Failed to load search index: {e}")
            self.search_index = {}
    
    def _load_index(self):
        """Carica l'indice dei documenti"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    
                for doc_data in index_data:
                    doc_data['created_at'] = datetime.fromisoformat(doc_data['created_at'])
                    doc_data['modified_at'] = datetime.fromisoformat(doc_data['modified_at'])
                    doc_data['type'] = DocumentType(doc_data['type'])
                    
                    doc = Document(**doc_data)
                    self.documents[doc.id] = doc
                
                self.logger.info(f"Loaded {len(self.documents)} documents from index")
            except Exception as e:
                self.logger.error(f"Failed to load document index: {e}")
                self.documents = {}
        else:
            self.logger.info("No existing document index found, starting with empty store")
    
    def _save_index(self):
        """Salva l'indice dei documenti"""
        try:
            index_data = [doc.to_dict() for doc in self.documents.values()]
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            self.logger.debug("Document index saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save document index: {e}")
            raise
    
    def _calculate_document_hash(self, content: str) -> str:
        """Calcola hash del contenuto documento"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _update_search_index(self, document: Document):
        """Aggiorna indice di ricerca full-text"""
        if not self.enable_search_index:
            return
        
        # Simple tokenization (può essere migliorata con libraries come nltk)
        words = set()
        
        # Tokenize title and content
        text = f"{document.title} {document.content}".lower()
        # Remove punctuation and split
        import re
        text = re.sub(r'[^\w\s]', ' ', text)
        words.update(word.strip() for word in text.split() if len(word.strip()) > 2)
        
        # Update index
        for word in words:
            if word not in self.search_index:
                self.search_index[word] = []
            
            if document.id not in self.search_index[word]:
                self.search_index[word].append(document.id)
        
        logger.debug(f"Search index updated for document {document.id}: {len(words)} terms")
    
    def _save_document_content(self, document: Document) -> str:
        """Salva contenuto documento su file"""
        try:
            # Create filename
            safe_title = "".join(c for c in document.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            filename = f"{document.id}_{safe_title}_v{document.version}.md"
            file_path = self.documents_path / filename
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                # Add metadata header
                f.write(f"---\n")
                f.write(f"id: {document.id}\n")
                f.write(f"title: {document.title}\n")
                f.write(f"type: {document.type.value}\n")
                f.write(f"version: {document.version}\n")
                f.write(f"created_at: {serialize_datetime(document.created_at)}\n")
                f.write(f"modified_at: {serialize_datetime(document.modified_at)}\n")
                f.write(f"author: {document.author}\n")
                f.write(f"project_id: {document.project_id}\n")
                f.write(f"---\n\n")
                f.write(document.content)
            
            document.file_path = str(file_path)
            logger.debug(f"Document content saved: {file_path}")
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save document content: {e}")
            raise StorageError(f"Failed to save document content: {e}")
    
    def _backup_document_version(self, document: Document):
        """Crea backup versione documento"""
        if not self.enable_versioning:
            return
        
        try:
            version_dir = self.versions_path / document.id
            version_dir.mkdir(exist_ok=True)
            
            version_file = version_dir / f"v{document.version}.json"
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(document.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Document version backed up: {version_file}")
            
        except Exception as e:
            logger.warning(f"Failed to backup document version: {e}")
    
    def _cleanup_old_versions(self, document_id: str):
        """Cleanup versioni vecchie se auto_cleanup abilitato"""
        if not self.auto_cleanup_versions or not self.enable_versioning:
            return
        
        try:
            version_dir = self.versions_path / document_id
            if not version_dir.exists():
                return
            
            version_files = list(version_dir.glob("v*.json"))
            if len(version_files) <= self.max_versions_per_document:
                return
            
            # Sort by version number and remove oldest
            version_files.sort(key=lambda f: int(f.stem[1:]))  # Remove 'v' prefix
            files_to_remove = version_files[:-self.max_versions_per_document]
            
            for file_path in files_to_remove:
                file_path.unlink()
                logger.debug(f"Cleaned up old version: {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup old versions: {e}")
    
    async def save_document(self, document: Document) -> str:
        """
        Salva documento (async per AutoGen compatibility)
        
        Args:
            document: Documento da salvare
            
        Returns:
            str: ID del documento salvato
            
        Raises:
            ValidationError: Se il documento non è valido
            StorageError: Se il salvataggio fallisce
        """
        # Validate document
        validate_document(document)
        
        with self._lock:
            try:
                # Check if document exists
                existing_doc = self.documents.get(document.id)
                
                if existing_doc:
                    existing_doc_copy = deepcopy(existing_doc)
                    new_hash = self._calculate_document_hash(document.content)
                    if existing_doc_copy.hash == new_hash:
                        logger.debug(f"Document {document.id} unchanged, skipping save")
                        return document.id
                    
                    # Increment version and update hash
                    document.version = existing_doc_copy.version + 1
                    document.hash = new_hash
                    document.modified_at = datetime.now()
                    
                    # Create change event
                    change_event = ChangeEvent(
                        document_id=document.id,
                        change_type=ChangeType.MODIFIED,
                        old_hash=existing_doc_copy.hash,
                        new_hash=document.hash,
                        description=f"Document {document.title} updated to v{document.version}",
                        author=document.author or "system"
                    )
                    
                    # Backup previous version using the copy
                    if self.enable_versioning:
                        self._backup_document_version(existing_doc_copy)

                else:
                    # New document
                    document.hash = self._calculate_document_hash(document.content)
                    if not document.created_at:
                        document.created_at = datetime.now()
                    document.modified_at = datetime.now()
                    
                    change_event = ChangeEvent(
                        document_id=document.id,
                        change_type=ChangeType.CREATED,
                        new_hash=document.hash,
                        description=f"Document {document.title} created (v{document.version})",
                        author=document.author or "system"
                    )
                
                # Save content to file
                await asyncio.get_event_loop().run_in_executor(
                    self._executor, 
                    self._save_document_content, 
                    document
                )
                
                # Update in-memory store
                self.documents[document.id] = document
                
                # Update search index
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._update_search_index,
                    document
                )
                
                # Save index
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._save_index
                )
                
                # Cleanup old versions
                if self.auto_cleanup_versions:
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        self._cleanup_old_versions,
                        document.id
                    )
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(change_event)
                        else:
                            callback(change_event)
                    except Exception as e:
                        logger.warning(f"Callback failed: {e}")
                
                # Add to AutoGen memory if available
                if self._memory_store and AUTOGEN_AVAILABLE:
                    await self._add_to_memory(document, change_event)
                
                logger.info(f"📄 Document saved: {document.title} (v{document.version})")
                return document.id
                
            except Exception as e:
                logger.error(f"Failed to save document {document.id}: {e}")
                raise StorageError(f"Failed to save document: {e}")
    
    async def get_document(self, document_id: str, version: Optional[int] = None) -> Optional[Document]:
        """
        Recupera documento per ID (async compatible)
        
        Args:
            document_id: ID del documento
            version: Versione specifica (None = latest)
            
        Returns:
            Optional[Document]: Documento o None se non trovato
        """
        with self._lock:
            if version is None:
                doc = self.documents.get(document_id)
                return deepcopy(doc) if doc else None
            
            # Load specific version
            if not self.enable_versioning:
                raise DocumentStoreError("Versioning not enabled")
            
            try:
                version_file = self.versions_path / document_id / f"v{version}.json"
                if not version_file.exists():
                    return None
                
                with open(version_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                
                return Document.from_dict(doc_data)
                
            except Exception as e:
                logger.error(f"Failed to load document version {document_id} v{version}: {e}")
                return None
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Elimina documento (async compatible)
        
        Args:
            document_id: ID del documento da eliminare
            
        Returns:
            bool: True se eliminato con successo
        """
        with self._lock:
            document = self.documents.get(document_id)
            if not document:
                return False
            
            try:
                # Remove from memory store
                del self.documents[document_id]
                
                # Remove from search index
                if self.enable_search_index:
                    for word, doc_ids in self.search_index.items():
                        if document_id in doc_ids:
                            doc_ids.remove(document_id)
                
                # Remove content file
                if document.file_path and Path(document.file_path).exists():
                    Path(document.file_path).unlink()
                
                # Remove version files
                if self.enable_versioning:
                    version_dir = self.versions_path / document_id
                    if version_dir.exists():
                        shutil.rmtree(version_dir)
                
                # Save updated index
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._save_index
                )
                
                # Create change event
                change_event = ChangeEvent(
                    document_id=document_id,
                    change_type=ChangeType.DELETED,
                    description=f"Document {document.title} deleted"
                )
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(change_event)
                        else:
                            callback(change_event)
                    except Exception as e:
                        logger.warning(f"Delete callback failed: {e}")
                
                logger.info(f"🗑️ Document deleted: {document.title}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete document {document_id}: {e}")
                return False
    
    async def search_documents(
        self,
        query: str,
        document_types: Optional[List[DocumentType]] = None,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Document]:
        """
        Ricerca full-text nei documenti (async compatible)
        
        Args:
            query: Query di ricerca
            document_types: Filtro per tipi documento
            project_id: Filtro per progetto
            limit: Numero massimo risultati
            
        Returns:
            List[Document]: Documenti trovati ordinati per rilevanza
        """
        if not self.enable_search_index:
            raise DocumentStoreError("Search index not enabled")
        
        with self._lock:
            try:
                query_words = set(word.lower().strip() for word in query.split() if len(word.strip()) > 2)
                if not query_words:
                    return []
                
                # Find matching documents
                document_scores: Dict[str, int] = {}
                
                for word in query_words:
                    if word in self.search_index:
                        for doc_id in self.search_index[word]:
                            document_scores[doc_id] = document_scores.get(doc_id, 0) + 1
                
                # Filter and sort results
                results = []
                for doc_id, score in sorted(document_scores.items(), key=lambda x: x[1], reverse=True):
                    document = self.documents.get(doc_id)
                    if not document:
                        continue
                    
                    # Apply filters
                    if document_types and document.type not in document_types:
                        continue
                    
                    if project_id and document.project_id != project_id:
                        continue
                    
                    results.append(document)
                    
                    if len(results) >= limit:
                        break
                
                logger.debug(f"Search '{query}' returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return []
    
    async def get_documents_by_type(self, document_type: DocumentType) -> List[Document]:
        """Recupera documenti per tipo (async compatible)"""
        with self._lock:
            return [doc for doc in self.documents.values() if doc.type == document_type]
    
    async def get_documents_by_project(self, project_id: str) -> List[Document]:
        """Recupera documenti per progetto (async compatible)"""
        with self._lock:
            return [doc for doc in self.documents.values() if doc.project_id == project_id]
    
    async def list_documents(self, 
                           include_metadata: bool = False,
                           sort_by: str = "modified_at",
                           reverse: bool = True) -> List[Document]:
        """Lista tutti i documenti con opzioni di sorting (async compatible)"""
        with self._lock:
            docs = list(self.documents.values())
            
            # Sort documents
            try:
                if sort_by == "modified_at":
                    docs.sort(key=lambda d: d.modified_at, reverse=reverse)
                elif sort_by == "created_at":
                    docs.sort(key=lambda d: d.created_at, reverse=reverse)
                elif sort_by == "title":
                    docs.sort(key=lambda d: d.title.lower(), reverse=reverse)
                elif sort_by == "version":
                    docs.sort(key=lambda d: d.version, reverse=reverse)
            except Exception as e:
                logger.warning(f"Sort failed, returning unsorted: {e}")
            
            return docs
    
    # ========================================================================
    # AUTOGEN 0.7.2+ INTEGRATION
    # ========================================================================
    
    async def integrate_with_memory(self, memory: Memory):
        """
        Integra con AutoGen Memory system
        
        Args:
            memory: AutoGen Memory instance
        """
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available, memory integration disabled")
            return
        
        self._memory_store = memory
        logger.info("Document Store integrated with AutoGen Memory")
    
    async def _add_to_memory(self, document: Document, change_event: ChangeEvent):
        """Aggiunge documento ad AutoGen Memory"""
        if not self._memory_store or not AUTOGEN_AVAILABLE:
            return
        
        try:
            # Create memory content
            memory_content = MemoryContent(
                content=f"Document: {document.title}\nType: {document.type.value}\nContent: {document.content[:500]}...",
                mime_type="text/markdown",
                metadata={
                    "document_id": document.id,
                    "document_type": document.type.value,
                    "version": document.version,
                    "project_id": document.project_id,
                    "change_type": change_event.change_type.value,
                    "timestamp": serialize_datetime(change_event.timestamp)
                }
            )
            
            await self._memory_store.add(memory_content)
            logger.debug(f"Document {document.id} added to memory")
            
        except Exception as e:
            logger.warning(f"Failed to add document to memory: {e}")
    
    def create_autogen_message(self, document: Document) -> TextMessage:
        """
        Crea AutoGen TextMessage da documento
        
        Args:
            document: Documento da convertire
            
        Returns:
            TextMessage: Messaggio AutoGen
        """
        if not AUTOGEN_AVAILABLE:
            raise DocumentStoreError("AutoGen not available")
        
        content = f"""# {document.title}

**Type**: {document.type.value}
**Version**: {document.version}
**Modified**: {document.modified_at.strftime('%Y-%m-%d %H:%M:%S')}

{document.content}
"""
        
        return TextMessage(
            content=content,
            source="DocumentStore",
            metadata={
                "document_id": document.id,
                "document_type": document.type.value,
                "version": document.version,
                "project_id": document.project_id
            }
        )
    
    async def get_documents_as_messages(
        self,
        document_ids: Optional[List[str]] = None,
        document_type: Optional[DocumentType] = None,
        project_id: Optional[str] = None
    ) -> List[TextMessage]:
        """
        Recupera documenti come AutoGen TextMessage
        
        Args:
            document_ids: Lista ID documenti specifici
            document_type: Filtro per tipo
            project_id: Filtro per progetto
            
        Returns:
            List[TextMessage]: Lista messaggi AutoGen
        """
        if not AUTOGEN_AVAILABLE:
            raise DocumentStoreError("AutoGen not available")
        
        messages = []
        
        with self._lock:
            if document_ids:
                documents = [self.documents.get(doc_id) for doc_id in document_ids]
                documents = [doc for doc in documents if doc is not None]
            else:
                documents = list(self.documents.values())
                
                # Apply filters
                if document_type:
                    documents = [doc for doc in documents if doc.type == document_type]
                
                if project_id:
                    documents = [doc for doc in documents if doc.project_id == project_id]
        
        for document in documents:
            try:
                message = self.create_autogen_message(document)
                messages.append(message)
            except Exception as e:
                logger.warning(f"Failed to create message for document {document.id}: {e}")
        
        return messages
    
    async def save_from_autogen_response(
        self,
        response: Response,
        document_type: DocumentType,
        project_id: Optional[str] = None,
        author: str = "autogen_agent"
    ) -> Optional[str]:
        """
        Salva documento da AutoGen Response
        
        Args:
            response: Response da agente AutoGen
            document_type: Tipo documento da creare
            project_id: ID progetto
            author: Autore del documento
            
        Returns:
            Optional[str]: ID documento creato o None
        """
        if not AUTOGEN_AVAILABLE:
            raise DocumentStoreError("AutoGen not available")
        
        try:
            if not hasattr(response, 'chat_message') or not response.chat_message:
                logger.warning("Response has no chat_message")
                return None
            
            message = response.chat_message
            if not hasattr(message, 'content'):
                logger.warning("Message has no content")
                return None
            
            content = message.content
            
            # Extract title from content (first line or default)
            lines = content.split('\n')
            title = lines[0].strip('#').strip() if lines else "Untitled Document"
            if len(title) > 100:
                title = title[:100] + "..."
            
            # Create document
            document = Document(
                id=generate_uuid(),
                type=document_type,
                title=title,
                content=content,
                version=1,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                hash="",
                dependencies=[],
                metadata={
                    "source": "autogen_agent",
                    "agent_name": getattr(message, 'source', 'unknown'),
                    "generated_at": serialize_datetime(datetime.now())
                },
                author=author,
                project_id=project_id
            )
            
            document_id = await self.save_document(document)
            logger.info(f"Document created from AutoGen response: {title}")
            
            return document_id
            
        except Exception as e:
            logger.error(f"Failed to save document from AutoGen response: {e}")
            return None
    
    def register_change_callback(self, callback: Callable[[ChangeEvent], Any]):
        """
        Registra callback per eventi di cambiamento
        
        Args:
            callback: Funzione da chiamare per ogni cambiamento
        """
        self._change_callbacks.append(callback)
        logger.debug(f"Change callback registered: {callback.__name__}")
    
    def unregister_change_callback(self, callback: Callable[[ChangeEvent], Any]):
        """Rimuove callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
            logger.debug(f"Change callback unregistered: {callback.__name__}")
    
    # ========================================================================
    # BACKUP & RECOVERY
    # ========================================================================
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Crea backup completo del document store
        
        Args:
            backup_name: Nome backup (auto-generato se None)
            
        Returns:
            str: Path del backup creato
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.backup_path / backup_name
        
        try:
            # Create backup directory
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy documents content
            content_backup = backup_dir / "content"
            if self.documents_path.exists():
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: shutil.copytree(self.documents_path, content_backup, dirs_exist_ok=True)
                )
            
            # Copy versions if enabled
            if self.enable_versioning and self.versions_path.exists():
                versions_backup = backup_dir / "versions"
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: shutil.copytree(self.versions_path, versions_backup, dirs_exist_ok=True)
                )
            
            # Copy index files
            if self.index_file.exists():
                shutil.copy2(self.index_file, backup_dir / "document_index.json")
            
            if self.enable_search_index and self.search_index_file.exists():
                shutil.copy2(self.search_index_file, backup_dir / "search_index.json")
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "created_at": serialize_datetime(datetime.now()),
                "document_count": len(self.documents),
                "storage_path": str(self.storage_path),
                "versioning_enabled": self.enable_versioning,
                "search_index_enabled": self.enable_search_index,
                "autogen_compatible": AUTOGEN_AVAILABLE
            }
            
            with open(backup_dir / "backup_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📦 Backup created: {backup_dir}")
            return str(backup_dir)
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise StorageError(f"Failed to create backup: {e}")
    
    async def restore_from_backup(self, backup_path: str) -> bool:
        """
        Ripristina da backup
        
        Args:
            backup_path: Path del backup
            
        Returns:
            bool: True se ripristinato con successo
        """
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            raise DocumentStoreError(f"Backup not found: {backup_path}")
        
        try:
            # Validate backup
            metadata_file = backup_dir / "backup_metadata.json"
            if not metadata_file.exists():
                raise DocumentStoreError("Invalid backup: missing metadata")
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Restoring from backup: {metadata.get('backup_name', 'Unknown')}")
            
            # Clear current storage
            with self._lock:
                self.documents.clear()
                self.search_index.clear()
            
            # Restore content
            content_backup = backup_dir / "content"
            if content_backup.exists():
                if self.documents_path.exists():
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        lambda: shutil.rmtree(self.documents_path)
                    )
                
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: shutil.copytree(content_backup, self.documents_path)
                )
            
            # Restore versions
            versions_backup = backup_dir / "versions"
            if self.enable_versioning and versions_backup.exists():
                if self.versions_path.exists():
                    await asyncio.get_event_loop().run_in_executor(
                        self._executor,
                        lambda: shutil.rmtree(self.versions_path)
                    )
                
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    lambda: shutil.copytree(versions_backup, self.versions_path)
                )
            
            # Restore index files
            backup_index = backup_dir / "document_index.json"
            if backup_index.exists():
                shutil.copy2(backup_index, self.index_file)
            
            backup_search_index = backup_dir / "search_index.json"
            if self.enable_search_index and backup_search_index.exists():
                shutil.copy2(backup_search_index, self.search_index_file)
            
            # Reload documents
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._load_index
            )
            
            logger.info(f"✅ Restore completed: {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise StorageError(f"Failed to restore from backup: {e}")
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """Lista tutti i backup disponibili"""
        backups = []
        
        try:
            if not self.backup_path.exists():
                return backups
            
            for backup_dir in self.backup_path.iterdir():
                if not backup_dir.is_dir():
                    continue
                
                metadata_file = backup_dir / "backup_metadata.json"
                if not metadata_file.exists():
                    continue
                
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Calculate backup size
                    total_size = sum(
                        f.stat().st_size 
                        for f in backup_dir.rglob('*') 
                        if f.is_file()
                    )
                    
                    backup_info = {
                        **metadata,
                        "backup_path": str(backup_dir),
                        "size_bytes": total_size,
                        "size_mb": round(total_size / (1024 * 1024), 2)
                    }
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to read backup metadata {backup_dir}: {e}")
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda b: b.get('created_at', ''), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    # ========================================================================
    # STATISTICS & MONITORING
    # ========================================================================
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Recupera statistiche del document store
        
        Returns:
            Dict: Statistiche complete
        """
        with self._lock:
            try:
                # Basic counts
                total_docs = len(self.documents)
                type_counts = {}
                project_counts = {}
                author_counts = {}
                total_content_size = 0
                
                for doc in self.documents.values():
                    # Type distribution
                    doc_type = doc.type.value
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                    
                    # Project distribution
                    if doc.project_id:
                        project_counts[doc.project_id] = project_counts.get(doc.project_id, 0) + 1
                    
                    # Author distribution
                    author = doc.author or "unknown"
                    author_counts[author] = author_counts.get(author, 0) + 1
                    
                    # Content size
                    total_content_size += len(doc.content)
                
                # Storage statistics
                storage_stats = await self._get_storage_statistics()
                
                # Search index statistics
                search_stats = {}
                if self.enable_search_index:
                    search_stats = {
                        "total_terms": len(self.search_index),
                        "avg_documents_per_term": (
                            sum(len(doc_ids) for doc_ids in self.search_index.values()) / len(self.search_index)
                            if self.search_index else 0
                        )
                    }
                
                # Recent activity
                recent_docs = sorted(
                    self.documents.values(),
                    key=lambda d: d.modified_at,
                    reverse=True
                )[:5]
                
                recent_activity = [
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "type": doc.type.value,
                        "modified_at": serialize_datetime(doc.modified_at),
                        "version": doc.version
                    }
                    for doc in recent_docs
                ]
                
                return {
                    "total_documents": total_docs,
                    "document_types": type_counts,
                    "projects": project_counts,
                    "authors": author_counts,
                    "content_size_bytes": total_content_size,
                    "content_size_mb": round(total_content_size / (1024 * 1024), 2),
                    "storage": storage_stats,
                    "search_index": search_stats,
                    "recent_activity": recent_activity,
                    "features": {
                        "versioning_enabled": self.enable_versioning,
                        "backup_enabled": self.enable_backup,
                        "search_index_enabled": self.enable_search_index,
                        "autogen_integration": AUTOGEN_AVAILABLE,
                        "auto_cleanup_enabled": self.auto_cleanup_versions
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to generate statistics: {e}")
                return {"error": str(e)}
    
    async def _get_storage_statistics(self) -> Dict[str, Any]:
        """Statistiche storage filesystem"""
        try:
            stats = {}
            
            # Documents directory
            if self.documents_path.exists():
                doc_files = list(self.documents_path.rglob("*.md"))
                doc_size = sum(f.stat().st_size for f in doc_files)
                stats["documents"] = {
                    "file_count": len(doc_files),
                    "total_size_bytes": doc_size,
                    "total_size_mb": round(doc_size / (1024 * 1024), 2)
                }
            
            # Versions directory
            if self.enable_versioning and self.versions_path.exists():
                version_files = list(self.versions_path.rglob("*.json"))
                version_size = sum(f.stat().st_size for f in version_files)
                stats["versions"] = {
                    "file_count": len(version_files),
                    "total_size_bytes": version_size,
                    "total_size_mb": round(version_size / (1024 * 1024), 2)
                }
            
            # Backup directory
            if self.enable_backup and self.backup_path.exists():
                backup_dirs = [d for d in self.backup_path.iterdir() if d.is_dir()]
                total_backup_size = 0
                for backup_dir in backup_dirs:
                    backup_size = sum(
                        f.stat().st_size 
                        for f in backup_dir.rglob('*') 
                        if f.is_file()
                    )
                    total_backup_size += backup_size
                
                stats["backups"] = {
                    "backup_count": len(backup_dirs),
                    "total_size_bytes": total_backup_size,
                    "total_size_mb": round(total_backup_size / (1024 * 1024), 2)
                }
            
            return stats
            
        except Exception as e:
            logger.warning(f"Failed to get storage statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Controllo salute del document store
        
        Returns:
            Dict: Report salute sistema
        """
        health = {
            "status": "healthy",
            "checks": {},
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Storage accessibility
            if not self.storage_path.exists() or not self.storage_path.is_dir():
                health["status"] = "unhealthy"
                health["issues"].append("Storage path not accessible")
            else:
                health["checks"]["storage_accessible"] = True
            
            # Index integrity
            try:
                if self.index_file.exists():
                    with open(self.index_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                    health["checks"]["index_valid"] = True
                else:
                    health["issues"].append("Index file missing")
            except json.JSONDecodeError:
                health["status"] = "degraded"
                health["issues"].append("Index file corrupted")
                health["recommendations"].append("Consider rebuilding index")
            
            # Document file consistency
            missing_files = 0
            for doc in self.documents.values():
                if doc.file_path and not Path(doc.file_path).exists():
                    missing_files += 1
            
            if missing_files > 0:
                health["status"] = "degraded"
                health["issues"].append(f"{missing_files} document files missing")
                health["recommendations"].append("Run document file repair")
            else:
                health["checks"]["document_files_consistent"] = True
            
            # Search index health
            if self.enable_search_index:
                try:
                    if self.search_index_file.exists():
                        with open(self.search_index_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                        health["checks"]["search_index_valid"] = True
                    else:
                        health["recommendations"].append("Rebuild search index")
                except json.JSONDecodeError:
                    health["issues"].append("Search index corrupted")
                    health["recommendations"].append("Rebuild search index")
            
            # AutoGen integration
            health["checks"]["autogen_available"] = AUTOGEN_AVAILABLE
            if not AUTOGEN_AVAILABLE:
                health["recommendations"].append("Install autogen-agentchat for full functionality")
            
            # Storage space
            import shutil as shutil_disk
            total, used, free = shutil_disk.disk_usage(self.storage_path)
            free_percent = (free / total) * 100
            
            health["checks"]["disk_space_ok"] = free_percent > 10
            if free_percent < 5:
                health["status"] = "critical"
                health["issues"].append("Very low disk space")
            elif free_percent < 10:
                health["status"] = "degraded"
                health["issues"].append("Low disk space")
                health["recommendations"].append("Consider cleanup or backup old documents")
            
            # Performance metrics
            health["metrics"] = {
                "total_documents": len(self.documents),
                "disk_usage_percent": round(100 - free_percent, 1),
                "index_size_mb": (
                    round(self.index_file.stat().st_size / (1024 * 1024), 2)
                    if self.index_file.exists() else 0
                )
            }
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["issues"].append(f"Health check failed: {e}")
        
        return health
    
    # ========================================================================
    # CLEANUP & MAINTENANCE
    # ========================================================================
    
    async def cleanup_orphaned_files(self) -> Dict[str, int]:
        """
        Pulisce file orfani nel storage
        
        Returns:
            Dict: Statistiche cleanup
        """
        cleanup_stats = {
            "orphaned_content_files": 0,
            "orphaned_version_files": 0,
            "empty_directories": 0,
            "space_freed_mb": 0
        }
        
        try:
            # Track valid files
            valid_files = set()
            
            # Add current document files
            for doc in self.documents.values():
                if doc.file_path:
                    valid_files.add(Path(doc.file_path))
            
            # Clean orphaned content files
            if self.documents_path.exists():
                for content_file in self.documents_path.rglob("*.md"):
                    if content_file not in valid_files:
                        size = content_file.stat().st_size
                        content_file.unlink()
                        cleanup_stats["orphaned_content_files"] += 1
                        cleanup_stats["space_freed_mb"] += size / (1024 * 1024)
            
            # Clean orphaned version directories
            if self.enable_versioning and self.versions_path.exists():
                valid_doc_ids = set(self.documents.keys())
                
                for version_dir in self.versions_path.iterdir():
                    if version_dir.is_dir() and version_dir.name not in valid_doc_ids:
                        # Calculate size before deletion
                        size = sum(
                            f.stat().st_size 
                            for f in version_dir.rglob('*') 
                            if f.is_file()
                        )
                        
                        shutil.rmtree(version_dir)
                        cleanup_stats["orphaned_version_files"] += len(list(version_dir.rglob("*.json")))
                        cleanup_stats["space_freed_mb"] += size / (1024 * 1024)
            
            # Remove empty directories
            for root_path in [self.documents_path, self.versions_path]:
                if root_path.exists():
                    for dirpath in root_path.rglob("*"):
                        if dirpath.is_dir() and not any(dirpath.iterdir()):
                            dirpath.rmdir()
                            cleanup_stats["empty_directories"] += 1
            
            cleanup_stats["space_freed_mb"] = round(cleanup_stats["space_freed_mb"], 2)
            
            logger.info(f"🧹 Cleanup completed: {cleanup_stats}")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            cleanup_stats["error"] = str(e)
        
        return cleanup_stats
    
    async def rebuild_search_index(self) -> Dict[str, Any]:
        """
        Ricostruisce l'indice di ricerca
        
        Returns:
            Dict: Statistiche ricostruzione
        """
        if not self.enable_search_index:
            raise DocumentStoreError("Search index not enabled")
        
        rebuild_stats = {
            "documents_processed": 0,
            "terms_indexed": 0,
            "processing_time_seconds": 0,
            "success": False
        }
        
        start_time = datetime.now()
        
        try:
            # Clear existing index
            self.search_index.clear()
            
            # Rebuild from all documents
            for document in self.documents.values():
                await asyncio.get_event_loop().run_in_executor(
                    self._executor,
                    self._update_search_index,
                    document
                )
                rebuild_stats["documents_processed"] += 1
            
            # Count total terms
            rebuild_stats["terms_indexed"] = len(self.search_index)
            
            # Save updated index
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                lambda: self._save_search_index()
            )
            
            rebuild_stats["processing_time_seconds"] = (datetime.now() - start_time).total_seconds()
            rebuild_stats["success"] = True
            
            logger.info(f"🔍 Search index rebuilt: {rebuild_stats}")
            
        except Exception as e:
            logger.error(f"Search index rebuild failed: {e}")
            rebuild_stats["error"] = str(e)
        
        return rebuild_stats
    
    def _save_search_index(self):
        """Helper per salvare search index"""
        if self.enable_search_index:
            with open(self.search_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_index, f, indent=2, ensure_ascii=False)
    
    def _save_search_index(self):
        """Helper per salvare search index"""
        if not self.enable_search_index:
            return
        try:
            with open(self.search_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_index, f, indent=2, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Failed to save search index: {e}")

    # ========================================================================
    # LIFECYCLE MANAGEMENT
    # ========================================================================
    
    async def close(self):
        """Chiude il document store e rilascia risorse"""
        try:
            # Save final state
            await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._save_index
            )
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            # Clear callbacks
            self._change_callbacks.clear()
            
            logger.info("Document Store closed")
            
        except Exception as e:
            logger.error(f"Error closing document store: {e}")
    
    def __len__(self) -> int:
        """Numero di documenti nel store"""
        return len(self.documents)
    
    def __contains__(self, document_id: str) -> bool:
        """Verifica se un documento esiste"""
        return document_id in self.documents
    
    def __iter__(self):
        """Itera su tutti i documenti"""
        return iter(self.documents.values())
    
    def __str__(self) -> str:
        """Rappresentazione string del document store"""
        return f"DocumentStore({len(self.documents)} documents, {self.storage_path})"
    
    def __repr__(self) -> str:
        """Rappresentazione tecnica del document store"""
        return (
            f"DocumentStore("
            f"path='{self.storage_path}', "
            f"docs={len(self.documents)}, "
            f"versioning={self.enable_versioning}, "
            f"search={self.enable_search_index}, "
            f"autogen={AUTOGEN_AVAILABLE}"
            f")"
        )


# ============================================================================
# DOCUMENT STORE FACTORY
# ============================================================================

class DocumentStoreFactory:
    """Factory per creare istanze di Document Store con configurazioni predefinite"""
    
    @staticmethod
    def create_default() -> DocumentStore:
        """Crea document store con configurazione di default"""
        return DocumentStore()
    
    @staticmethod
    def create_production(storage_path: str) -> DocumentStore:
        """Crea document store per ambiente produzione"""
        return DocumentStore(
            storage_path=storage_path,
            enable_versioning=True,
            enable_backup=True,
            enable_search_index=True,
            auto_cleanup_versions=True,
            max_versions_per_document=5
        )
    
    @staticmethod
    def create_development(storage_path: str = "dev_documents") -> DocumentStore:
        """Crea document store per sviluppo"""
        return DocumentStore(
            storage_path=storage_path,
            enable_versioning=True,
            enable_backup=False,
            enable_search_index=True,
            auto_cleanup_versions=False,
            max_versions_per_document=10
        )
    
    @staticmethod
    def create_testing(storage_path: str = "test_documents") -> DocumentStore:
        """Crea document store per testing"""
        return DocumentStore(
            storage_path=storage_path,
            enable_versioning=False,
            enable_backup=False,
            enable_search_index=False,
            auto_cleanup_versions=False,
            max_concurrent_operations=5
        )
    
    @staticmethod
    def create_memory_only() -> DocumentStore:
        """Crea document store solo in memoria (per testing veloce)"""
        import tempfile
        temp_dir = tempfile.mkdtemp(prefix="docstore_memory_")
        
        return DocumentStore(
            storage_path=temp_dir,
            enable_versioning=False,
            enable_backup=False,
            enable_search_index=False,
            auto_cleanup_versions=False
        )


# ============================================================================
# AUTOGEN 0.7.2+ UTILITY FUNCTIONS
# ============================================================================

async def create_document_from_task_result(
    task_result: TaskResult,
    document_type: DocumentType,
    project_id: Optional[str] = None,
    author: str = "autogen_team"
) -> Optional[Document]:
    """
    Crea documento da AutoGen TaskResult
    
    Args:
        task_result: Risultato da team AutoGen
        document_type: Tipo documento da creare
        project_id: ID progetto
        author: Autore documento
        
    Returns:
        Optional[Document]: Documento creato o None
    """
    if not AUTOGEN_AVAILABLE:
        raise DocumentStoreError("AutoGen not available")
    
    try:
        if not task_result.messages:
            return None
        
        # Combina tutti i messaggi in un unico contenuto
        content_parts = []
        title = "Generated Document"
        
        for message in task_result.messages:
            if hasattr(message, 'content') and message.content:
                # Prendi il primo messaggio come titolo
                if not title or title == "Generated Document":
                    first_line = message.content.split('\n')[0].strip()
                    if first_line:
                        title = first_line.strip('#').strip()[:100]
                
                # Aggiungi source se disponibile
                source_prefix = ""
                if hasattr(message, 'source') and message.source:
                    source_prefix = f"**{message.source}**: "
                
                content_parts.append(f"{source_prefix}{message.content}")
        
        if not content_parts:
            return None
        
        content = "\n\n---\n\n".join(content_parts)
        
        document = Document(
            id=generate_uuid(),
            type=document_type,
            title=title,
            content=content,
            version=1,
            created_at=datetime.now(),
            modified_at=datetime.now(),
            hash="",
            dependencies=[],
            metadata={
                "source": "autogen_team",
                "message_count": len(task_result.messages),
                "generated_at": serialize_datetime(datetime.now()),
                "stop_reason": getattr(task_result, 'stop_reason', 'unknown')
            },
            author=author,
            project_id=project_id
        )
        
        return document
        
    except Exception as e:
        logger.error(f"Failed to create document from TaskResult: {e}")
        return None


def get_autogen_compatibility_info() -> Dict[str, Any]:
    """
    Restituisce informazioni compatibilità AutoGen 0.7.2+
    
    Returns:
        Dict: Info compatibilità
    """
    return {
        "autogen_available": AUTOGEN_AVAILABLE,
        "supported_features": [
            "TextMessage integration",
            "Response processing", 
            "TaskResult processing",
            "Memory integration",
            "Async/await patterns",
            "Change callbacks"
        ] if AUTOGEN_AVAILABLE else [],
        "required_version": ">=0.4.0",
        "recommended_version": ">=0.7.2",
        "compatibility_level": "full" if AUTOGEN_AVAILABLE else "none"
    }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core classes
    'DocumentStore',
    'DocumentStoreFactory',
    
    # Exceptions
    'DocumentStoreError',
    'DocumentNotFoundError', 
    'DocumentVersionConflictError',
    'StorageError',
    'IndexCorruptedError',
    
    # AutoGen utilities
    'create_document_from_task_result',
    'get_autogen_compatibility_info',
    
    # Compatibility
    'AUTOGEN_AVAILABLE'
]