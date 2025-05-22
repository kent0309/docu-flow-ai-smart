
// Mock API configuration
const API_BASE_URL = 'mock-api';

export const API_ENDPOINTS = {
  // Document endpoints (mock)
  DOCUMENTS: `${API_BASE_URL}/documents/`,
  DOCUMENT_DETAIL: (id: string) => `${API_BASE_URL}/documents/${id}/`,
  DOCUMENT_SUMMARIZE: (id: string) => `${API_BASE_URL}/documents/${id}/summarize/`,
  DOCUMENT_EXTRACT: (id: string) => `${API_BASE_URL}/documents/${id}/extract/`,
  
  // Processed document endpoints (mock)
  PROCESSED_DOCUMENTS: `${API_BASE_URL}/processed-documents/`,
  PROCESSED_DOCUMENT_DETAIL: (id: string) => `${API_BASE_URL}/processed-documents/${id}/`,
  
  // ML endpoints (mock)
  ML_TRAIN: `${API_BASE_URL}/ml/train/`,
  ML_STATS: `${API_BASE_URL}/ml/stats/`,
};

// Mock backend available - always returns true since we're using mock data
export const checkBackendAvailability = async (): Promise<boolean> => {
  return true;
};

// Helper function to simulate authentication
export const getAuthToken = (): string | null => {
  return 'mock-auth-token';
};

// Common headers for API requests
export const getCommonHeaders = () => {
  return {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer mock-auth-token'
  };
};

// Import the DocumentType from mock.service to ensure type consistency
import { DocumentType, DocumentStatus } from "@/services/mock.service";

// Mock data functions
export const getMockDocuments = () => {
  return [
    {
      id: '1',
      filename: 'Invoice-May2025-12345.pdf',
      type: 'invoice' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'May 8, 2025',
      confidence: 98
    },
    {
      id: '2',
      filename: 'Contract-ServiceAgreement.pdf',
      type: 'contract' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'May 7, 2025',
      confidence: 95
    },
    {
      id: '3',
      filename: 'Receipt-Office-Supplies.jpg',
      type: 'receipt' as DocumentType,
      status: 'processing' as DocumentStatus,
      date: 'May 8, 2025'
    },
    {
      id: '4',
      filename: 'Invoice-April2025-45678.pdf',
      type: 'invoice' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'Apr 29, 2025',
      confidence: 92
    },
    {
      id: '5',
      filename: 'Contract-NDA-Client123.pdf',
      type: 'contract' as DocumentType,
      status: 'error' as DocumentStatus,
      date: 'May 6, 2025'
    },
    {
      id: '6',
      filename: 'Receipt-Travel-Expenses.jpg',
      type: 'receipt' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'May 3, 2025',
      confidence: 90
    },
    {
      id: '7',
      filename: 'Invoice-March2025-98765.pdf',
      type: 'invoice' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'Mar 15, 2025',
      confidence: 97
    },
    {
      id: '8',
      filename: 'Report-Q1-2025.pdf',
      type: 'report' as DocumentType,
      status: 'processed' as DocumentStatus,
      date: 'Apr 10, 2025',
      confidence: 94
    }
  ];
};

// Mock ML stats
export const getMockMLStats = () => {
  return {
    accuracy: 92.5,
    totalDocuments: 1248,
    classDistribution: {
      invoice: 524,
      contract: 312,
      receipt: 289,
      report: 103,
      other: 20
    },
    lastTrainingDate: 'May 5, 2025',
    confidenceThreshold: 85
  };
};
