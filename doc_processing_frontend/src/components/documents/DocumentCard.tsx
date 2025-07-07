import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { FileText, FileSpreadsheet, FileImage, Mail, FileCode, FilePenLine, File } from 'lucide-react';
import { Document } from '@/lib/api';

interface DocumentCardProps {
  document: Document;
  onClick?: () => void;
}

const DocumentCard: React.FC<DocumentCardProps> = ({ document, onClick }) => {
  // Helper function to get icon based on document type
  const getDocumentIcon = () => {
    const type = document.document_type?.toLowerCase() || 'unknown';
    
    if (type === 'email' || document.document_subtype === 'email') {
      return <Mail className="h-10 w-10 text-blue-500" />;
    } else if (type === 'invoice' || type === 'receipt') {
      return <FileSpreadsheet className="h-10 w-10 text-green-500" />;
    } else if (type === 'form') {
      return <FilePenLine className="h-10 w-10 text-purple-500" />;
    } else if (type === 'contract' || type === 'legal') {
      return <FileText className="h-10 w-10 text-amber-500" />;
    } else if (type === 'report') {
      return <FileCode className="h-10 w-10 text-cyan-500" />;
    } else {
      return <File className="h-10 w-10 text-gray-500" />;
    }
  };
  
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
  
  // Format document type for display
  const getFormattedDocumentType = () => {
    if (document.document_type === 'unknown' || !document.document_type) {
      return 'Unknown Type';
    }

    // Check for email subtype
    if (document.document_type === 'email' || document.document_subtype === 'email') {
      return 'Email';
    }
    
    // Capitalize the document type
    return document.document_type.charAt(0).toUpperCase() + document.document_type.slice(1);
  };

  return (
    <Card 
      className="cursor-pointer transition-all hover:bg-muted/50 group overflow-hidden"
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg line-clamp-1 group-hover:text-primary">
            {document.filename}
          </CardTitle>
          <Badge className={`${getStatusColor(document.status)} text-white`}>
            {document.status}
          </Badge>
        </div>
        <CardDescription className="flex justify-between">
          <span>{document.date}</span>
          {document.confidence !== undefined && (
            <span className="text-xs">
              AI Confidence: {document.confidence}%
            </span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center py-6">
        {getDocumentIcon()}
      </CardContent>
      <CardFooter className="bg-muted/50 py-2 px-6 flex justify-center">
        <span className="text-sm font-medium text-muted-foreground">
          {getFormattedDocumentType()}
        </span>
      </CardFooter>
    </Card>
  );
}

export default DocumentCard;
