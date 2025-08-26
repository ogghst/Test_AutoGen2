import React, { useState } from 'react';
import { ScrollArea } from './ui/scroll-area';
import ReactMarkdown from 'react-markdown';

interface Document {
  id: string;
  title: string;
  content: string;
}

const placeholderDocs: Document[] = [
  { id: '1', title: 'Project Charter', content: '# Project Charter\n\nThis is the project charter.' },
  { id: '2', title: 'Requirements Document', content: '# Requirements\n\n- Requirement 1\n- Requirement 2' },
  { id: '3', title: 'Meeting Notes', content: '# Meeting Notes\n\n## 2025-08-25\n\n- Discussed UI refactoring.' },
];

const DocumentSidebar: React.FC = () => {
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(placeholderDocs[0]);

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Documents</h2>
      </div>
      <div className="flex flex-grow">
        <ScrollArea className="w-1/3 border-r">
          <div className="p-4 space-y-2">
            {placeholderDocs.map((doc) => (
              <button
                key={doc.id}
                className={`w-full text-left p-2 rounded-md ${
                  selectedDoc?.id === doc.id ? 'bg-accent' : ''
                }`}
                onClick={() => setSelectedDoc(doc)}
              >
                {doc.title}
              </button>
            ))}
          </div>
        </ScrollArea>
        <ScrollArea className="w-2/3">
          <div className="p-4">
            {selectedDoc ? (
              <ReactMarkdown>{selectedDoc.content}</ReactMarkdown>
            ) : (
              <p className="text-muted-foreground">Select a document to view its content.</p>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default DocumentSidebar;
