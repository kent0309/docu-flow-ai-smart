
import { toast } from "sonner";
import { getMockDocuments, getMockMLStats } from "@/config/api";

export type DocumentType = 'invoice' | 'contract' | 'receipt' | 'report' | 'other';
export type DocumentStatus = 'processing' | 'processed' | 'error';

export interface Document {
  id: string;
  filename: string;
  type: DocumentType;
  status: DocumentStatus;
  date: string;
  confidence?: number;
}

export interface ExtractedField {
  name: string;
  value: string;
  confidence: number;
  isValid: boolean;
}

export interface ExtractionResult {
  documentType: string;
  fields: ExtractedField[];
}

// Fetch all documents (mock)
export const fetchDocuments = async (): Promise<Document[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  return getMockDocuments();
};

// Process uploaded files (mock)
export const processFiles = async (files: File[]): Promise<boolean> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Show success toast
  toast.success(`${files.length} file${files.length !== 1 ? 's' : ''} processed successfully`);
  
  return true;
};

// Extract data from document (mock)
export const extractDocumentData = async (documentId: string): Promise<ExtractionResult> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock extraction result
  return {
    documentType: "invoice",
    fields: [
      { name: "Invoice Number", value: "INV-2025-0042", confidence: 98, isValid: true },
      { name: "Date", value: "2025-05-15", confidence: 95, isValid: true },
      { name: "Total Amount", value: "$1,245.67", confidence: 92, isValid: true },
      { name: "Vendor", value: "Tech Supplies Inc", confidence: 89, isValid: true },
      { name: "Due Date", value: "2025-06-15", confidence: 76, isValid: false },
      { name: "Tax Amount", value: "$98.76", confidence: 85, isValid: true }
    ]
  };
};

// Get ML statistics (mock)
export const getMLStats = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 700));
  return getMockMLStats();
};

// Train ML model (mock)
export const trainModel = async (): Promise<boolean> => {
  // Simulate longer API delay for training
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Show success toast
  toast.success('Model trained successfully');
  
  return true;
};
