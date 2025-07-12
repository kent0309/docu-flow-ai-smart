import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDistanceToNow } from 'date-fns';
import { Download, Loader2 } from 'lucide-react';
import { getDocument } from '@/lib/api';

interface DocumentDetailViewProps {
  document: any; // Replace with proper type when available
  isOpen: boolean;
  onClose: () => void;
}

const DocumentDetailView: React.FC<DocumentDetailViewProps> = ({ document, isOpen, onClose }) => {
  // Fetch full document details when modal is opened
  const { data: fullDocument, isLoading, error } = useQuery({
    queryKey: ['document', document?.id],
    queryFn: () => getDocument(document.id),
    enabled: isOpen && !!document?.id,
  });

  // Use full document data if available, otherwise fall back to passed document
  const documentData = fullDocument || document;

  if (!document) return null;
  
  // Add download functionality using the working method
  const handleDownload = async () => {
    try {
      console.log('Starting download for document:', document.id);
      const downloadUrl = `/api/documents/${document.id}/export-csv/`;
      
      // Try opening in a new window/tab (this method works)
      const newWindow = window.open(downloadUrl, '_blank');
      
      if (!newWindow) {
        // If popup blocked, try direct navigation
        window.location.href = downloadUrl;
      }
      
      console.log('Download initiated successfully');
      
      // Show success message
      setTimeout(() => {
        alert(`CSV file download started successfully!`);
      }, 500);
      
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };
  
  // Format the uploaded date
  const formattedDate = documentData.uploaded_at 
    ? formatDistanceToNow(new Date(documentData.uploaded_at), { addSuffix: true })
    : 'Unknown';
  
  // Helper function to get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'bg-green-500';
      case 'processing':
        return 'bg-blue-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };
  
  // Function to render extracted data based on type
  const renderExtractedData = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading document details...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-8 text-destructive">
          <p>Error loading document details: {error.message}</p>
        </div>
      );
    }

    console.log('Document extracted_data:', documentData.extracted_data);
    console.log('Extracted data keys:', documentData.extracted_data ? Object.keys(documentData.extracted_data) : 'No data');
    
    // Check if we have extracted data
    if (!documentData.extracted_data || Object.keys(documentData.extracted_data).length === 0) {
      return (
        <div className="space-y-4">
          <p className="text-muted-foreground">No data has been extracted from this document.</p>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Document Status Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2">
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Status:</span>
                  <span className="col-span-2">{documentData.status}</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Document Type:</span>
                  <span className="col-span-2">{documentData.document_type || 'Unknown'}</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Language:</span>
                  <span className="col-span-2">{documentData.detected_language || 'Unknown'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    // We have extracted data, now display it properly
    const extractedData = documentData.extracted_data;
    
    return (
      <div className="space-y-4">
        {/* Dynamic data display for all document types */}
        {(() => {
          // Get all extracted data keys excluding technical fields
          const excludedKeys = ['raw_text', 'validation_results', 'confidence_score', 'extraction_time'];
          
          const dataKeys = Object.keys(extractedData)
            .filter(key => !excludedKeys.includes(key) && extractedData[key] !== null && extractedData[key] !== undefined);
            
          if (dataKeys.length > 0) {
            return (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">Extracted Information</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-3">
                  {dataKeys.map(key => {
                    const value = extractedData[key];
                    
                    // Handle arrays
                    if (Array.isArray(value)) {
                      if (value.length === 0) return null;
                      return (
                        <div key={key} className="grid grid-cols-4 gap-1">
                          <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                          <span className="col-span-3">{value.join(', ')}</span>
                        </div>
                      );
                    }
                    
                    // Handle objects (but not null)
                    if (typeof value === 'object' && value !== null) {
                      return (
                        <div key={key} className="grid grid-cols-4 gap-1">
                          <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                          <span className="col-span-3">
                            <pre className="text-sm bg-muted p-2 rounded text-wrap">
                              {JSON.stringify(value, null, 2)}
                            </pre>
                          </span>
                        </div>
                      );
                    }
                    
                    // Handle empty values
                    if (value === '' || value === null || value === undefined) {
                      return null;
                    }
                    
                    // Handle simple values
                    const formattedKey = key
                      .replace(/_/g, ' ')
                      .split(' ')
                      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                      .join(' ');
                      
                    return (
                      <div key={key} className="grid grid-cols-4 gap-1">
                        <span className="font-medium">{formattedKey}:</span>
                        <span className="col-span-3">
                          {typeof value === 'number' && key.toLowerCase().includes('amount') 
                            ? `$${value.toFixed(2)}` 
                            : String(value)}
                        </span>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            );
          }
          return null;
        })()}

        {/* Raw extracted text */}
        {extractedData.raw_text && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">
                Extracted Text 
                {extractedData.raw_text.confidence && (
                  <span className="text-sm font-normal text-muted-foreground ml-2">
                    (Confidence: {extractedData.raw_text.confidence})
                  </span>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px] rounded-md border p-4 bg-muted/30">
                <pre className="whitespace-pre-wrap text-sm">
                  {typeof extractedData.raw_text === 'string' 
                    ? extractedData.raw_text 
                    : extractedData.raw_text.value || JSON.stringify(extractedData.raw_text, null, 2)}
                </pre>
              </ScrollArea>
            </CardContent>
          </Card>
        )}

        {/* Validation Results */}
        {extractedData.validation_results && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Validation Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2">
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Status:</span>
                  <span className="col-span-2">{extractedData.validation_results.status}</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Total Rules:</span>
                  <span className="col-span-2">{extractedData.validation_results.total_rules}</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Passed Rules:</span>
                  <span className="col-span-2">{extractedData.validation_results.passed_rules}</span>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  <span className="font-medium">Failed Rules:</span>
                  <span className="col-span-2">{extractedData.validation_results.failed_rules}</span>
                </div>
                {extractedData.validation_results.warnings && 
                 extractedData.validation_results.warnings.length > 0 && (
                  <div className="grid grid-cols-3 gap-1">
                    <span className="font-medium">Warnings:</span>
                    <span className="col-span-2">{extractedData.validation_results.warnings.join(', ')}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Debug section - show all raw data */}
        <details className="group">
          <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
            Show all raw extracted data (Debug)
          </summary>
          <Card className="mt-2">
            <CardContent className="pt-4">
              <ScrollArea className="h-[200px] rounded-md border p-4 bg-muted/30">
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(extractedData, null, 2)}
                </pre>
              </ScrollArea>
            </CardContent>
          </Card>
        </details>
      </div>
    );
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-xl">{documentData.filename}</span>
            <Badge className={`${getStatusColor(documentData.status)} text-white`}>
              {documentData.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Uploaded {formattedDate} • {documentData.document_type || 'Unknown type'}
          </DialogDescription>
        </DialogHeader>
        
        <ScrollArea className="flex-1 mt-4">
          <Tabs defaultValue="data">
            <TabsList className="mb-4">
              <TabsTrigger value="data">Extracted Data</TabsTrigger>
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="metadata">Metadata</TabsTrigger>
            </TabsList>
            
            <TabsContent value="data" className="space-y-4">
              {renderExtractedData()}
            </TabsContent>
            
            <TabsContent value="summary">
              {documentData.summary ? (
                <Card>
                  <CardContent className="pt-4">
                    <p>{documentData.summary}</p>
                  </CardContent>
                </Card>
              ) : (
                <p className="text-muted-foreground">No summary available for this document.</p>
              )}
            </TabsContent>
            
            <TabsContent value="metadata">
              <Card>
                <CardContent className="pt-4">
                  <div className="grid gap-2">
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">ID:</span>
                      <span className="col-span-2 break-all">{documentData.id}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">File Name:</span>
                      <span className="col-span-2">{documentData.filename}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Status:</span>
                      <span className="col-span-2">{documentData.status}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Document Type:</span>
                      <span className="col-span-2">{documentData.document_type || 'Unknown'}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Language:</span>
                      <span className="col-span-2">{documentData.detected_language || 'Unknown'}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Uploaded:</span>
                      <span className="col-span-2">{documentData.uploaded_at ? new Date(documentData.uploaded_at).toLocaleString() : 'Unknown'}</span>
                    </div>
                    {documentData.extracted_data?.confidence_score !== undefined && (
                      <div className="grid grid-cols-3 gap-1">
                        <span className="font-medium">Confidence Score:</span>
                        <span className="col-span-2">{documentData.extracted_data.confidence_score * 100}%</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </ScrollArea>
        
        <DialogFooter className="mt-6">
          <Button variant="outline" onClick={onClose}>Close</Button>
          <Button onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download CSV
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentDetailView; 