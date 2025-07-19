import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getDocument } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface UseDocumentPollingProps {
  documentId: string;
  documentName: string;
  initialStatus: string;
  enabled?: boolean;
}

export const useDocumentPolling = ({ 
  documentId, 
  documentName, 
  initialStatus, 
  enabled = true 
}: UseDocumentPollingProps) => {
  const [isPolling, setIsPolling] = useState(false);
  const [currentStatus, setCurrentStatus] = useState(initialStatus);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  useEffect(() => {
    // Only start polling if enabled and document is in processing state
    if (enabled && initialStatus === 'processing') {
      startPolling();
    }

    return () => {
      stopPolling();
    };
  }, [enabled, initialStatus]);

  const startPolling = () => {
    if (isPolling) return;
    
    setIsPolling(true);
    console.log(`Starting polling for document: ${documentName} (${documentId})`);
    
    const pollDocument = async () => {
      try {
        const document = await getDocument(documentId);
        const newStatus = document.status;
        
        // If status changed from processing to processed, show notification
        if (newStatus === 'processed' && currentStatus === 'processing') {
          // Show a more prominent notification
          toast({
            title: "🎉 Document Processing Complete!",
            description: `"${documentName}" has been successfully processed and is ready for review.`,
            duration: 8000, // Show for 8 seconds
          });
          
          // Also show a browser notification if supported
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Document Processing Complete', {
              body: `"${documentName}" has been successfully processed.`,
              icon: '/favicon.ico',
              tag: `doc-${documentId}`,
            });
          }
          
          // Invalidate and refetch documents list to update UI
          queryClient.invalidateQueries({ queryKey: ['documents'] });
          
          // Stop polling
          stopPolling();
          return;
        }
        
        // If status is error, stop polling
        if (newStatus === 'error' && currentStatus === 'processing') {
          toast({
            title: "Processing Error",
            description: `Document '${documentName}' encountered an error during processing.`,
            variant: "destructive",
          });
          
          // Invalidate and refetch documents list to update UI
          queryClient.invalidateQueries({ queryKey: ['documents'] });
          
          // Stop polling
          stopPolling();
          return;
        }
        
        // Update current status
        setCurrentStatus(newStatus);
        
      } catch (error) {
        console.error('Error polling document status:', error);
        // Don't stop polling on network errors, just log them
      }
    };

    // Poll every 3 seconds
    pollingIntervalRef.current = setInterval(pollDocument, 3000);
    
    // Initial poll
    pollDocument();
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setIsPolling(false);
    console.log(`Stopped polling for document: ${documentName} (${documentId})`);
  };

  return {
    isPolling,
    currentStatus,
    startPolling,
    stopPolling,
  };
}; 