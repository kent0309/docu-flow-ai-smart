import React from 'react';
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

interface DocumentDetailViewProps {
  document: any; // Replace with proper type when available
  isOpen: boolean;
  onClose: () => void;
}

const DocumentDetailView: React.FC<DocumentDetailViewProps> = ({ document, isOpen, onClose }) => {
  if (!document) return null;
  
  // Format the uploaded date
  const formattedDate = document.uploaded_at 
    ? formatDistanceToNow(new Date(document.uploaded_at), { addSuffix: true })
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
    if (!document.extracted_data) {
      return <p className="text-muted-foreground">No data has been extracted from this document.</p>;
    }

    // Check if we have an email document
    const isEmailDocument = document.document_type === 'Email' || document.document_type === 'email';
    
    // Extract all keys except these technical/internal fields
    const excludedKeys = ['raw_text', 'error', 'validation_result', 'extraction_time', 
                        'file_type', 'confidence_score', 'body', 'items'];
                        
    // Get all extracted data keys to display
    const extractedDataKeys = Object.keys(document.extracted_data)
      .filter(key => !excludedKeys.includes(key));
      
    return (
      <div className="space-y-4">
        {/* Display the extracted data dynamically as key-value pairs */}
        {extractedDataKeys.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Extracted Data</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              {extractedDataKeys.map(key => {
                const value = document.extracted_data[key];
                // Skip rendering arrays/objects in the main section (they'll be shown separately)
                if (typeof value === 'object' && value !== null) return null;
                
                // Format the key for display (capitalize, replace underscores with spaces)
                const formattedKey = key
                  .replace(/_/g, ' ')
                  .split(' ')
                  .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                  .join(' ');
                  
                return (
                  <div key={key} className="grid grid-cols-3 gap-1">
                    <span className="font-medium">{formattedKey}:</span>
                    <span className="col-span-2">
                      {typeof value === 'number' && key.toLowerCase().includes('amount') 
                        ? `$${value.toFixed(2)}` 
                        : String(value)}
                    </span>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        )}
        
        {/* Render email body if present */}
        {isEmailDocument && document.extracted_data.body && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Email Body</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border rounded-md p-4 bg-muted/20 whitespace-pre-wrap text-sm">
                {document.extracted_data.body}
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* Render line items if present */}
        {document.extracted_data.items && document.extracted_data.items.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Line Items</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="border rounded-md overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted text-muted-foreground">
                    <tr>
                      <th className="p-2 text-left">Description</th>
                      <th className="p-2 text-right">Qty</th>
                      <th className="p-2 text-right">Price</th>
                      <th className="p-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {document.extracted_data.items.map((item: any, idx: number) => (
                      <tr key={idx} className="border-t">
                        <td className="p-2">{item.description}</td>
                        <td className="p-2 text-right">{item.quantity}</td>
                        <td className="p-2 text-right">
                          ${typeof item.unit_price === 'number' 
                            ? item.unit_price.toFixed(2) 
                            : item.unit_price}
                        </td>
                        <td className="p-2 text-right">
                          ${typeof item.total === 'number' 
                            ? item.total.toFixed(2) 
                            : (item.quantity * item.unit_price).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
        
        {/* Show raw text if available */}
        {document.extracted_data.raw_text && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Extracted Text</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px] rounded-md border p-4 bg-muted/30">
                <pre className="whitespace-pre-wrap text-sm">
                  {document.extracted_data.raw_text}
                </pre>
              </ScrollArea>
            </CardContent>
          </Card>
        )}
        
        {/* Show all raw extracted data for debugging */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Raw Extracted Data</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px] rounded-md border p-4 bg-muted/30">
              <pre className="whitespace-pre-wrap text-sm">
                {JSON.stringify(document.extracted_data, null, 2)}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    );
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <span className="text-xl">{document.filename}</span>
            <Badge className={`${getStatusColor(document.status)} text-white`}>
              {document.status}
            </Badge>
          </DialogTitle>
          <DialogDescription>
            Uploaded {formattedDate} • {document.document_type || 'Unknown type'}
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
              {document.summary ? (
                <Card>
                  <CardContent className="pt-4">
                    <p>{document.summary}</p>
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
                      <span className="col-span-2 break-all">{document.id}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">File Name:</span>
                      <span className="col-span-2">{document.filename}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Status:</span>
                      <span className="col-span-2">{document.status}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Document Type:</span>
                      <span className="col-span-2">{document.document_type || 'Unknown'}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Language:</span>
                      <span className="col-span-2">{document.detected_language || 'Unknown'}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-1">
                      <span className="font-medium">Uploaded:</span>
                      <span className="col-span-2">{document.uploaded_at ? new Date(document.uploaded_at).toLocaleString() : 'Unknown'}</span>
                    </div>
                    {document.extracted_data?.confidence_score !== undefined && (
                      <div className="grid grid-cols-3 gap-1">
                        <span className="font-medium">Confidence Score:</span>
                        <span className="col-span-2">{document.extracted_data.confidence_score * 100}%</span>
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
          <Button>Download</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentDetailView; 