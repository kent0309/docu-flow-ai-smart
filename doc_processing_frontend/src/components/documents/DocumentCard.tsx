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
  FileCode,
  File
} from 'lucide-react';

export type DocumentStatus = 'processing' | 'processed' | 'error';
export type DocumentType = 'invoice' | 'contract' | 'receipt' | 'report' | 'other';

export interface DocumentCardProps {
  id: string;
  filename: string;
  type: DocumentType;
  status: DocumentStatus;
  date: string;
  confidence?: number;
}

const getDocumentIcon = (type: DocumentType) => {
  switch (type) {
    case 'invoice':
      return <FileSpreadsheet className="h-6 w-6" />;
    case 'contract':
      return <FileText className="h-6 w-6" />;
    case 'receipt':
      return <FileCode className="h-6 w-6" />;
    default:
      return <File className="h-6 w-6" />;
  }
};

const getStatusIcon = (status: DocumentStatus) => {
  switch (status) {
    case 'processing':
      return <Clock className="h-4 w-4 text-blue-500" />;
    case 'processed':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'error':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    default:
      return null;
  }
};

const getStatusColor = (status: DocumentStatus) => {
  switch (status) {
    case 'processing':
      return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    case 'processed':
      return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    case 'error':
      return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    default:
      return "";
  }
};

const DocumentCard = ({ 
  id, 
  filename, 
  type, 
  status, 
  date, 
  confidence = 0 
}: DocumentCardProps) => {
  return (
    <Card className="overflow-hidden transition-all hover:shadow-md">
      <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
        <div className="flex items-center space-x-2">
          <div className="rounded-md bg-primary/10 p-2">
            {getDocumentIcon(type)}
          </div>
          <div>
            <p className="text-sm font-medium">{type.charAt(0).toUpperCase() + type.slice(1)}</p>
          </div>
        </div>
        <Badge variant="outline" className={getStatusColor(status)}>
          <div className="flex items-center gap-1">
            {getStatusIcon(status)}
            <span>{status.charAt(0).toUpperCase() + status.slice(1)}</span>
          </div>
        </Badge>
      </CardHeader>
      <CardContent className="p-4 pt-2">
        <h3 className="font-medium truncate" title={filename}>
          {filename}
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Uploaded on {date}
        </p>
        
        {status === 'processed' && (
          <div className="mt-3">
            <div className="flex justify-between text-xs mb-1">
              <span>AI Confidence</span>
              <span>{confidence}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-1.5">
              <div 
                className="h-1.5 rounded-full bg-primary" 
                style={{ width: `${confidence}%` }}
              ></div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="p-4 pt-0 gap-2">
        <Button variant="outline" size="sm" className="flex-1">
          <Eye className="h-3.5 w-3.5 mr-1" />
          <span>View</span>
        </Button>
        <Button variant="outline" size="sm" className="flex-1">
          <Download className="h-3.5 w-3.5 mr-1" />
          <span>Download</span>
        </Button>
        <Button variant="ghost" size="icon" className="ml-auto">
          <MoreVertical className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
};

export default DocumentCard;
