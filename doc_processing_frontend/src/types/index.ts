
export type DocumentStatus = 'processing' | 'processed' | 'error' | 'pending';
export type DocumentType = 'invoice' | 'contract' | 'receipt' | 'report' | 'other';

export interface Document {
  id: string;
  filename: string;
  type: DocumentType;
  status: DocumentStatus;
  uploadDate: string;
  processedDate?: string;
  confidence?: number;
  extractedData?: Record<string, any>;
  fileSize: number;
  fileType: string;
}

export interface ProcessingStats {
  totalDocuments: number;
  processed: number;
  processing: number;
  errors: number;
  averageProcessingTime: number;
  accuracyRate: number;
}

export interface UploadedFile extends File {
  id: string;
  preview?: string;
  uploadProgress?: number;
  status?: 'uploading' | 'uploaded' | 'error';
}
