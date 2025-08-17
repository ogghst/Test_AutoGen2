"""
Test suite for the DocumentStore class.

This suite covers all major functionalities of the DocumentStore, including:
- Basic CRUD (Create, Read, Update, Delete) operations.
- Indexing and file persistence.
- Document versioning and retrieval of specific versions.
- Full-text search with filtering capabilities.
- Listing and sorting documents.
- Backup and restore functionality.
- Maintenance tasks like cleaning up orphaned files.
- Statistics and health checks.
- Factory for creating store instances.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List

# Try to import pytest, but don't fail if it's not available
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a mock pytest module for unittest compatibility
    class MockPytest:
        def mark(self, *args, **kwargs):
            return lambda func: func
    pytest = MockPytest()

from tests.base_test import AsyncBaseTestCase, PerformanceTestCase
from storage.document_store import (
    DocumentStore,
    DocumentStoreFactory,
    DocumentNotFoundError,
    ValidationError,
    StorageError,
)
from models.data_models import (
    Document,
    DocumentType,
    ChangeEvent,
    ChangeType,
    generate_uuid,
)


class TestDocumentStore(AsyncBaseTestCase):
    """Test suite for DocumentStore class"""
    
    def setup_test_environment(self):
        """Set up test environment for document store tests."""
        self.storage_path = self.test_dir / "docstore"
        self.store = DocumentStore(storage_path=str(self.storage_path))
        
        # Test data
        self.sample_document = Document(
            id=generate_uuid(),
            title="Test Document 1",
            content="This is the content of the test document.",
            type=DocumentType.TECHNICAL_SPEC,
            author="test_runner",
            project_id="proj_123",
        )
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    
    def test_initialization(self):
        """Test that the document store initializes correctly."""
        self.assertEqual(self.store.storage_path, self.storage_path)
        self.assertFalse(self.store.index_file.exists())
        self.assertEqual(len(self.store), 0)
    



    async def test_save_and_get_document(self):
        """Test saving a new document and retrieving it."""
        doc_id = await self.store.save_document(self.sample_document)
        self.assertEqual(doc_id, self.sample_document.id)
        self.assertEqual(len(self.store), 1)
        self.assertTrue(self.store.index_file.exists())

        retrieved_doc = await self.store.get_document(doc_id)
        self.assertIsNotNone(retrieved_doc)
        self.assertEqual(retrieved_doc.id, doc_id)
        self.assertEqual(retrieved_doc.title, self.sample_document.title)
        self.assertEqual(retrieved_doc.content, self.sample_document.content)
        self.assertEqual(retrieved_doc.version, 1)
        self.assertIsNotNone(retrieved_doc.hash)
        self.assertNotEqual(retrieved_doc.hash, "")
    



    async def test_save_document_updates_existing(self):
        """Test that saving a document with the same ID updates it and increments the version."""
        await self.store.save_document(self.sample_document)
        self.assertEqual((await self.store.get_document(self.sample_document.id)).version, 1)

        doc_to_update = await self.store.get_document(self.sample_document.id)
        doc_to_update.content = "This is the updated content."
        await self.store.save_document(doc_to_update)

        self.assertEqual(len(self.store), 1)
        retrieved_doc = await self.store.get_document(self.sample_document.id)
        self.assertIsNotNone(retrieved_doc)
        self.assertEqual(retrieved_doc.content, "This is the updated content.")
        self.assertEqual(retrieved_doc.version, 2)
    



    async def test_save_document_no_change(self):
        """Test that saving a document without changes doesn't create a new version."""
        await self.store.save_document(self.sample_document)
        retrieved_doc_v1 = await self.store.get_document(self.sample_document.id)
        self.assertEqual(retrieved_doc_v1.version, 1)

        await self.store.save_document(retrieved_doc_v1)
        retrieved_doc_v2 = await self.store.get_document(self.sample_document.id)
        self.assertEqual(retrieved_doc_v2.version, 1)
    



    async def test_get_non_existent_document(self):
        """Test that getting a non-existent document returns None."""
        retrieved_doc = await self.store.get_document("non_existent_id")
        self.assertIsNone(retrieved_doc)
    



    async def test_delete_document(self):
        """Test deleting a document and its associated file."""
        await self.store.save_document(self.sample_document)
        self.assertEqual(len(self.store), 1)
        
        doc_file_path = Path((await self.store.get_document(self.sample_document.id)).file_path)
        self.assertTrue(doc_file_path.exists())

        deleted = await self.store.delete_document(self.sample_document.id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.store), 0)
        self.assertIsNone(await self.store.get_document(self.sample_document.id))
        self.assertFalse(doc_file_path.exists())
    



    async def test_save_invalid_document(self):
        """Test that saving a document with missing required fields raises ValidationError."""
        invalid_doc = Document(id="123", title=" ", content="c", type=DocumentType.API_DOCUMENTATION)
        with self.assertRaises(ValidationError):
            await self.store.save_document(invalid_doc)
    



    async def test_index_persistence(self):
        """Test that the index is saved and loaded across different DocumentStore instances."""
        store1 = DocumentStore(storage_path=str(self.storage_path))
        await store1.save_document(self.sample_document)
        await store1.close()

        store2 = DocumentStore(storage_path=str(self.storage_path))
        self.assertEqual(len(store2), 1)
        retrieved_doc = await store2.get_document(self.sample_document.id)
        self.assertIsNotNone(retrieved_doc)
        self.assertEqual(retrieved_doc.id, self.sample_document.id)
        await store2.close()


class TestDocumentStoreVersioning(AsyncBaseTestCase):
    """Test suite for DocumentStore versioning features"""
    
    def setup_test_environment(self):
        """Set up test environment for versioning tests."""
        self.storage_path = self.test_dir / "docstore_versioning"
        self.store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_versioning=True,
            enable_search_index=True,
            enable_backup=True
        )
        
        self.sample_document = Document(
            id=generate_uuid(),
            title="Versioned Document",
            content="Original content",
            type=DocumentType.TECHNICAL_SPEC,
            author="test_runner",
            project_id="proj_123",
        )
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    



    async def test_versioning_creates_backup(self):
        """Test that updating a document creates a version backup."""
        await self.store.save_document(self.sample_document)  # v1

        doc_to_update = await self.store.get_document(self.sample_document.id)
        doc_to_update.content = "New content for version 2"
        await self.store.save_document(doc_to_update)  # v2

        version_dir = self.store.versions_path / self.sample_document.id
        self.assertTrue(version_dir.exists())
        version_file = version_dir / "v1.json"
        self.assertTrue(version_file.exists())

        with open(version_file, 'r') as f:
            v1_data = json.load(f)
            self.assertEqual(v1_data['version'], 1)
            self.assertEqual(v1_data['content'], "Original content")
    



    async def test_get_specific_version(self):
        """Test retrieving a specific older version of a document."""
        original_content = self.sample_document.content
        await self.store.save_document(self.sample_document)  # v1

        doc_to_update = await self.store.get_document(self.sample_document.id)
        doc_to_update.content = "Newer content"
        await self.store.save_document(doc_to_update)  # v2

        latest_doc = await self.store.get_document(self.sample_document.id)
        self.assertEqual(latest_doc.version, 2)
        self.assertEqual(latest_doc.content, "Newer content")

        v1_doc = await self.store.get_document(self.sample_document.id, version=1)
        self.assertIsNotNone(v1_doc)
        self.assertEqual(v1_doc.version, 1)
        self.assertEqual(v1_doc.content, original_content)
    



    async def test_version_cleanup(self):
        """Test that old versions are cleaned up automatically."""
        store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_versioning=True,
            auto_cleanup_versions=True,
            max_versions_per_document=2
        )

        # Save v1
        await store.save_document(self.sample_document)
        # Save v2
        doc_v2 = await store.get_document(self.sample_document.id)
        doc_v2.content = "v2"
        await store.save_document(doc_v2)
        # Save v3
        doc_v3 = await store.get_document(self.sample_document.id)
        doc_v3.content = "v3"
        await store.save_document(doc_v3)
        # Save v4
        doc_v4 = await store.get_document(self.sample_document.id)
        doc_v4.content = "v4"
        await store.save_document(doc_v4)

        version_dir = store.versions_path / self.sample_document.id
        version_files = sorted(list(version_dir.glob("*.json")), key=lambda f: int(f.stem[1:]))
        
        self.assertEqual(len(version_files), 2)
        self.assertEqual(version_files[0].name, "v2.json")
        self.assertEqual(version_files[1].name, "v3.json")
        self.assertFalse((version_dir / "v1.json").exists())
        await store.close()


class TestDocumentStoreSearch(AsyncBaseTestCase):
    """Test suite for DocumentStore search features"""
    
    def setup_test_environment(self):
        """Set up test environment for search tests."""
        self.storage_path = self.test_dir / "docstore_search"
        self.store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_search_index=True
        )
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    



    async def test_search_documents(self):
        """Test full-text search functionality."""
        doc1 = Document(id="d1", title="Python Code", content="This document contains python code examples.", type=DocumentType.TECHNICAL_SPEC, project_id="p1")
        doc2 = Document(id="d2", title="Java Examples", content="This document is about Java programming.", type=DocumentType.TECHNICAL_SPEC, project_id="p1")
        doc3 = Document(id="d3", title="Project Plan", content="A plan for the python project.", type=DocumentType.PROJECT_PLAN, project_id="p2")
        
        await self.store.save_document(doc1)
        await self.store.save_document(doc2)
        await self.store.save_document(doc3)

        results = await self.store.search_documents("python")
        self.assertEqual(len(results), 2)
        self.assertEqual({doc.id for doc in results}, {"d1", "d3"})
    



    async def test_search_with_filters(self):
        """Test search with document_type and project_id filters."""
        doc1 = Document(id="d1", title="Python Code", content="doc python", type=DocumentType.TECHNICAL_SPEC, project_id="p1")
        doc2 = Document(id="d2", title="Java Examples", content="doc java", type=DocumentType.TECHNICAL_SPEC, project_id="p1")
        doc3 = Document(id="d3", title="Python Plan", content="doc python plan", type=DocumentType.PROJECT_PLAN, project_id="p2")
        await self.store.save_document(doc1)
        await self.store.save_document(doc2)
        await self.store.save_document(doc3)

        results = await self.store.search_documents("python", document_types=[DocumentType.PROJECT_PLAN])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "d3")

        results = await self.store.search_documents("doc", project_id="p1")
        self.assertEqual(len(results), 2)
        self.assertEqual({doc.id for doc in results}, {"d1", "d2"})


class TestDocumentStoreListing(AsyncBaseTestCase):
    """Test suite for DocumentStore listing features"""
    
    def setup_test_environment(self):
        """Set up test environment for listing tests."""
        self.storage_path = self.test_dir / "docstore_listing"
        self.store = DocumentStore(storage_path=str(self.storage_path))
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    



    async def test_list_documents_sorting(self):
        """Test listing all documents with various sorting options."""
        doc1 = Document(id="d1", title="C Doc", content="c", type=DocumentType.TECHNICAL_SPEC, created_at=datetime(2023, 1, 1))
        await self.store.save_document(doc1)
        await asyncio.sleep(0.01)
        doc2 = Document(id="d2", title="A Doc", content="a", type=DocumentType.PROJECT_PLAN, created_at=datetime(2023, 1, 3))
        await self.store.save_document(doc2)
        await asyncio.sleep(0.01)
        doc3 = Document(id="d3", title="B Doc", content="b", type=DocumentType.API_DOCUMENTATION, created_at=datetime(2023, 1, 2))
        await self.store.save_document(doc3)

        docs = await self.store.list_documents()
        self.assertEqual([d.id for d in docs], ["d3", "d2", "d1"])

        docs = await self.store.list_documents(sort_by="title", reverse=False)
        self.assertEqual([d.id for d in docs], ["d2", "d3", "d1"])

        docs = await self.store.list_documents(sort_by="created_at", reverse=False)
        self.assertEqual([d.id for d in docs], ["d1", "d3", "d2"])
    



    async def test_get_documents_by_type(self):
        """Test getting documents filtered by type."""
        doc1 = Document(id="d1", title="Spec", content="c", type=DocumentType.TECHNICAL_SPEC)
        doc2 = Document(id="d2", title="Plan", content="a", type=DocumentType.PROJECT_PLAN)
        doc3 = Document(id="d3", title="Another Spec", content="d", type=DocumentType.TECHNICAL_SPEC)
        await self.store.save_document(doc1)
        await self.store.save_document(doc2)
        await self.store.save_document(doc3)

        specs = await self.store.get_documents_by_type(DocumentType.TECHNICAL_SPEC)
        self.assertEqual(len(specs), 2)
        self.assertEqual({d.id for d in specs}, {"d1", "d3"})
    



    async def test_get_documents_by_project(self):
        """Test getting documents filtered by project ID."""
        doc1 = Document(id="d1", title="Spec", content="c", type=DocumentType.TECHNICAL_SPEC, project_id="p1")
        doc2 = Document(id="d2", title="Plan", content="a", type=DocumentType.PROJECT_PLAN, project_id="p2")
        doc3 = Document(id="d3", title="API", content="b", type=DocumentType.API_DOCUMENTATION, project_id="p1")
        await self.store.save_document(doc1)
        await self.store.save_document(doc2)
        await self.store.save_document(doc3)

        p1_docs = await self.store.get_documents_by_project("p1")
        self.assertEqual(len(p1_docs), 2)
        self.assertEqual({d.id for d in p1_docs}, {"d1", "d3"})


class TestDocumentStoreBackup(AsyncBaseTestCase):
    """Test suite for DocumentStore backup features"""
    
    def setup_test_environment(self):
        """Set up test environment for backup tests."""
        self.storage_path = self.test_dir / "docstore_backup"
        self.store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_backup=True
        )
        
        self.sample_document = Document(
            id=generate_uuid(),
            title="Backup Test Document",
            content="This document will be backed up and restored.",
            type=DocumentType.TECHNICAL_SPEC,
            author="test_runner",
            project_id="proj_123",
        )
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    



    async def test_create_and_list_backup(self):
        """Test creating a backup and listing it."""
        await self.store.save_document(self.sample_document)
        
        backup_path_str = await self.store.create_backup("test_backup_1")
        self.assertTrue(Path(backup_path_str).exists())

        backups = await self.store.list_backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0]["backup_name"], "test_backup_1")
    



    async def test_restore_from_backup(self):
        """Test restoring the store's state from a backup."""
        await self.store.save_document(self.sample_document)
        backup_path = await self.store.create_backup("restore_test")

        await self.store.delete_document(self.sample_document.id)
        self.assertEqual(len(self.store), 0)

        restored = await self.store.restore_from_backup(backup_path)
        self.assertTrue(restored)
        
        self.assertEqual(len(self.store), 1)
        restored_doc = await self.store.get_document(self.sample_document.id)
        self.assertIsNotNone(restored_doc)
        self.assertEqual(restored_doc.title, self.sample_document.title)


class TestDocumentStoreMaintenance(AsyncBaseTestCase):
    """Test suite for DocumentStore maintenance features"""
    
    def setup_test_environment(self):
        """Set up test environment for maintenance tests."""
        self.storage_path = self.test_dir / "docstore_maintenance"
        self.store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_versioning=True,
            enable_backup=True
        )
        
        self.sample_document = Document(
            id=generate_uuid(),
            title="Maintenance Test Document",
            content="This document will be used for maintenance tests.",
            type=DocumentType.TECHNICAL_SPEC,
            author="test_runner",
            project_id="proj_123",
        )
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    



    async def test_cleanup_orphaned_files(self):
        """Test cleanup of orphaned content and version files."""
        await self.store.save_document(self.sample_document)

        orphaned_content_file = self.store.documents_path / "orphaned_content.md"
        orphaned_content_file.write_text("orphan")
        
        orphaned_version_dir = self.store.versions_path / "orphaned_doc_id"
        orphaned_version_dir.mkdir()
        (orphaned_version_dir / "v1.json").write_text("{}")

        stats = await self.store.cleanup_orphaned_files()

        self.assertEqual(stats["orphaned_content_files"], 1)
        self.assertFalse(orphaned_content_file.exists())
        self.assertFalse(orphaned_version_dir.exists())
    



    async def test_get_statistics(self):
        """Test if statistics are calculated correctly."""
        await self.store.save_document(self.sample_document)
        
        stats = await self.store.get_statistics()
        
        self.assertEqual(stats["total_documents"], 1)
        self.assertEqual(stats["document_types"][DocumentType.TECHNICAL_SPEC.value], 1)
        self.assertEqual(stats["projects"]["proj_123"], 1)
        self.assertEqual(stats["authors"]["test_runner"], 1)
        self.assertEqual(stats["content_size_bytes"], len(self.sample_document.content))
    



    async def test_health_check(self):
        """Test the health check functionality."""
        health = await self.store.health_check()
        self.assertEqual(health["status"], "healthy")
        
        self.store.index_file.write_text("{not_a_valid_json")
        health_degraded = await self.store.health_check()
        self.assertEqual(health_degraded["status"], "degraded")
        self.assertIn("Index file corrupted", health_degraded["issues"])


class TestDocumentStoreFactory(AsyncBaseTestCase):
    """Test suite for DocumentStoreFactory class"""
    
    def setup_test_environment(self):
        """Set up test environment for factory tests."""
        self.storage_path = self.test_dir / "docstore_factory"
    


    def test_document_store_factory(self):
        """Test the DocumentStoreFactory creates instances with correct settings."""
        # Create the necessary directories first
        self.storage_path.mkdir(exist_ok=True)
        
        test_path = self.storage_path / "testing"
        testing_store = DocumentStoreFactory.create_testing(storage_path=str(test_path))
        self.assertIsInstance(testing_store, DocumentStore)
        self.assertEqual(testing_store.storage_path, test_path)
        self.assertFalse(testing_store.enable_versioning)
        self.assertFalse(testing_store.enable_search_index)

        dev_path = self.storage_path / "development"
        dev_store = DocumentStoreFactory.create_development(storage_path=str(dev_path))
        self.assertTrue(dev_store.enable_versioning)
        self.assertTrue(dev_store.enable_search_index)
        self.assertFalse(dev_store.auto_cleanup_versions)

        mem_store = DocumentStoreFactory.create_memory_only()
        self.assertIsInstance(mem_store, DocumentStore)
        self.assertTrue(mem_store.storage_path.exists())
        import shutil
        shutil.rmtree(mem_store.storage_path)


class TestDocumentStorePerformance(PerformanceTestCase):
    """Test suite for DocumentStore performance"""
    
    def setup_test_environment(self):
        """Set up test environment for performance tests."""
        self.storage_path = self.test_dir / "docstore_performance"
        self.store = DocumentStore(
            storage_path=str(self.storage_path),
            enable_search_index=True
        )
        self.set_performance_threshold(2.0)  # 2 seconds for performance tests
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            asyncio.run(self.store.close())
    


    def test_bulk_operations_performance(self):
        """Test performance of bulk document operations."""
        # Create many test documents
        documents = []
        for i in range(100):
            doc = Document(
                id=f"perf_doc_{i}",
                title=f"Performance Document {i}",
                content=f"This is performance test document number {i} with some content to make it realistic.",
                type=DocumentType.TECHNICAL_SPEC,
                author="perf_tester",
                project_id=f"proj_{i % 10}"
            )
            documents.append(doc)
        
        # Measure bulk save performance
        def save_documents():
            for doc in documents:
                asyncio.run(self.store.save_document(doc))
        
        execution_time = self.measure_performance(save_documents)
        self.assert_performance(execution_time, self.performance_threshold, "Bulk document save")
        
        # Measure search performance
        def search_documents():
            asyncio.run(self.store.search_documents("performance"))
        
        execution_time = self.measure_performance(search_documents)
        self.assert_performance(execution_time, self.performance_threshold, "Document search")
