
import React from 'react';
import DocumentCard, { DocumentCardProps } from './DocumentCard';

interface DocumentGridProps {
  documents: DocumentCardProps[];
}

const DocumentGrid = ({ documents }: DocumentGridProps) => {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-muted p-6 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
        </div>
        <h3 className="text-xl font-medium mb-1">No documents found</h3>
        <p className="text-muted-foreground max-w-sm">
          Upload documents to start processing and analyzing them with our AI system.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {documents.map((doc) => (
        <DocumentCard key={doc.id} {...doc} />
      ))}
    </div>
  );
};

export default DocumentGrid;
