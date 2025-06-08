
import React from 'react';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Eye, 
  Download, 
  MoreVertical,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  FileSpreadsheet,
  Image,
  File
} from 'lucide-react';
import { Document } from '@/types';

interface DocumentCardProps {
  document: Document;
  onView?: (id: string) => void;
  onDownload?: (id: string) => void;
  onDelete?: (id: string) => void;
}

const getDocumentIcon = (type: string) => {
  switch (type) {
    case 'invoice':
      return <FileSpreadsheet className="h-6 w-6" />;
    case 'contract':
      return <FileText className="h-6 w-6" />;
    case 'receipt':
      return <Image className="h-6 w-6" />;
    default:
      return <File className="h-6 w-6" />;
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'processing':
      return <Clock className="h-4 w-4 text-blue-500" />;
    case 'processed':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'error':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    default:
      return <Clock className="h-4 w-4 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'processing':
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    case 'processed':
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    case 'error':
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400";
  }
};

const DocumentCard = ({ 
  document, 
  onView, 
  onDownload, 
  onDelete 
}: DocumentCardProps) => {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center space-x-2">
          <div className="rounded-md bg-primary/10 p-2">
            {getDocumentIcon(document.type)}
          </div>
          <div>
            <p className="text-sm font-medium capitalize">{document.type}</p>
          </div>
        </div>
        <Badge variant="outline" className={getStatusColor(document.status)}>
          <div className="flex items-center gap-1">
            {getStatusIcon(document.status)}
            <span className="capitalize">{document.status}</span>
          </div>
        </Badge>
      </CardHeader>
      <CardContent className="p-4 pt-2">
        <h3 className="font-medium truncate" title={document.filename}>
          {document.filename}
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Uploaded on {new Date(document.uploadDate).toLocaleDateString()}
        </p>
        
        {document.status === 'processed' && document.confidence && (
          <div className="mt-3">
            <div className="flex justify-between text-xs mb-1">
              <span>AI Confidence</span>
              <span>{document.confidence}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-1.5">
              <div 
                className="h-1.5 rounded-full bg-primary" 
                style={{ width: `${document.confidence}%` }}
              ></div>
            </div>
          </div>
        )}
        
        {document.extractedData && (
          <div className="mt-3 p-2 bg-muted rounded text-xs">
            <p className="font-medium mb-1">Extracted Data:</p>
            <pre className="text-xs text-muted-foreground truncate">
              {JSON.stringify(document.extractedData, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
      <CardFooter className="p-4 pt-0 gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="flex-1"
          onClick={() => onView?.(document.id)}
        >
          <Eye className="h-3.5 w-3.5 mr-1" />
          View
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          className="flex-1"
          onClick={() => onDownload?.(document.id)}
        >
          <Download className="h-3.5 w-3.5 mr-1" />
          Download
        </Button>
        <Button variant="ghost" size="icon" className="ml-auto">
          <MoreVertical className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DocumentCard;
