import React, { useEffect, useState } from 'react';
import { useDocumentPolling } from '@/hooks/use-document-polling';

interface DocumentPollingManagerProps {
  documents: Array<{ id: string; name: string; status: string }>;
}

const DocumentPollingManager: React.FC<DocumentPollingManagerProps> = ({ documents }) => {
  const [localDocuments, setLocalDocuments] = useState(documents);

  // Update local documents when props change
  useEffect(() => {
    setLocalDocuments(documents);
  }, [documents]);

  // Create polling instances for each processing document
  const processingDocuments = localDocuments.filter(doc => doc.status === 'processing');

  return (
    <>
      {processingDocuments.map(doc => (
        <DocumentPoller
          key={doc.id}
          documentId={doc.id}
          documentName={doc.name}
          initialStatus={doc.status}
          onStatusChange={(newStatus) => {
            setLocalDocuments(prev => 
              prev.map(d => 
                d.id === doc.id ? { ...d, status: newStatus } : d
              )
            );
          }}
        />
      ))}
    </>
  );
};

interface DocumentPollerProps {
  documentId: string;
  documentName: string;
  initialStatus: string;
  onStatusChange?: (newStatus: string) => void;
}

const DocumentPoller: React.FC<DocumentPollerProps> = ({ 
  documentId, 
  documentName, 
  initialStatus,
  onStatusChange
}) => {
  const { currentStatus } = useDocumentPolling({
    documentId,
    documentName,
    initialStatus,
    enabled: true
  });

  // Notify parent of status changes
  useEffect(() => {
    if (onStatusChange && currentStatus !== initialStatus) {
      onStatusChange(currentStatus);
    }
  }, [currentStatus, initialStatus, onStatusChange]);

  return null; // This component doesn't render anything
};

export default DocumentPollingManager; 