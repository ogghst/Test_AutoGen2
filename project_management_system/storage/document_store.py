import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..models.data_models import Document, DocumentType


class DocumentStore:
    """Store per documenti di output generati dagli agenti"""
    
    def __init__(self, storage_path: str = "documents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.index_file = self.storage_path / "document_index.json"
        self.documents: Dict[str, Document] = {}
        self._load_index()
    
    def _load_index(self):
        """Carica l'indice dei documenti"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                
            for doc_data in index_data:
                doc_data['created_at'] = datetime.fromisoformat(doc_data['created_at'])
                doc_data['modified_at'] = datetime.fromisoformat(doc_data['modified_at'])
                doc_data['type'] = DocumentType(doc_data['type'])
                
                doc = Document(**doc_data)
                self.documents[doc.id] = doc
    
    def _save_index(self):
        """Salva l'indice dei documenti"""
        index_data = [doc.to_dict() for doc in self.documents.values()]
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def save_document(self, document: Document) -> None:
        """Salva un documento e aggiorna l'indice"""
        # Calcola hash del contenuto
        document.hash = hashlib.md5(document.content.encode()).hexdigest()
        document.modified_at = datetime.now()
        
        # Salva contenuto su file
        doc_file = self.storage_path / f"{document.id}_v{document.version}.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(document.content)
        
        # Aggiorna indice
        self.documents[document.id] = document
        self._save_index()
        
        print(f"📄 Documento salvato: {document.title} (v{document.version})")
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Recupera un documento per ID"""
        return self.documents.get(doc_id)
    
    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Recupera documenti per tipo"""
        return [doc for doc in self.documents.values() if doc.type == doc_type]
    
    def list_documents(self) -> List[Document]:
        """Lista tutti i documenti"""
        return list(self.documents.values())
