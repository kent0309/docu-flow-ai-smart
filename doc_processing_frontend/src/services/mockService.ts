
import { Document, ProcessingStats, DocumentType, DocumentStatus } from '@/types';

// Mock data
const mockDocuments: Document[] = [
  {
    id: '1',
    filename: 'Invoice-2024-001.pdf',
    type: 'invoice',
    status: 'processed',
    uploadDate: '2024-01-15',
    processedDate: '2024-01-15',
    confidence: 95,
    fileSize: 245760,
    fileType: 'application/pdf',
    extractedData: {
      invoiceNumber: 'INV-2024-001',
      amount: 1250.00,
      vendor: 'Tech Solutions Inc.',
      date: '2024-01-15'
    }
  },
  {
    id: '2',
    filename: 'Contract-ServiceAgreement.pdf',
    type: 'contract',
    status: 'processed',
    uploadDate: '2024-01-14',
    processedDate: '2024-01-14',
    confidence: 92,
    fileSize: 567890,
    fileType: 'application/pdf',
    extractedData: {
      contractType: 'Service Agreement',
      parties: ['Company A', 'Company B'],
      duration: '12 months',
      value: 50000
    }
  },
  {
    id: '3',
    filename: 'Receipt-Office-Supplies.jpg',
    type: 'receipt',
    status: 'processing',
    uploadDate: '2024-01-16',
    fileSize: 123456,
    fileType: 'image/jpeg'
  },
  {
    id: '4',
    filename: 'Report-Q4-2023.pdf',
    type: 'report',
    status: 'error',
    uploadDate: '2024-01-13',
    fileSize: 890123,
    fileType: 'application/pdf'
  },
  {
    id: '5',
    filename: 'Invoice-2024-002.pdf',
    type: 'invoice',
    status: 'processed',
    uploadDate: '2024-01-12',
    processedDate: '2024-01-12',
    confidence: 98,
    fileSize: 198765,
    fileType: 'application/pdf',
    extractedData: {
      invoiceNumber: 'INV-2024-002',
      amount: 750.00,
      vendor: 'Office Supplies Co.',
      date: '2024-01-12'
    }
  }
];

const mockStats: ProcessingStats = {
  totalDocuments: 245,
  processed: 240,
  processing: 3,
  errors: 2,
  averageProcessingTime: 45, // seconds
  accuracyRate: 96.5
};

// Mock API functions
export const mockService = {
  // Get all documents
  getDocuments: async (): Promise<Document[]> => {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
    return mockDocuments;
  },

  // Get documents by status
  getDocumentsByStatus: async (status: DocumentStatus): Promise<Document[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockDocuments.filter(doc => doc.status === status);
  },

  // Get documents by type
  getDocumentsByType: async (type: DocumentType): Promise<Document[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockDocuments.filter(doc => doc.type === type);
  },

  // Get single document
  getDocument: async (id: string): Promise<Document | null> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockDocuments.find(doc => doc.id === id) || null;
  },

  // Upload document (mock)
  uploadDocument: async (file: File): Promise<Document> => {
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate upload time
    
    const newDoc: Document = {
      id: Math.random().toString(36).substr(2, 9),
      filename: file.name,
      type: 'other',
      status: 'processing',
      uploadDate: new Date().toISOString().split('T')[0],
      fileSize: file.size,
      fileType: file.type
    };
    
    mockDocuments.unshift(newDoc);
    return newDoc;
  },

  // Delete document
  deleteDocument: async (id: string): Promise<boolean> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const index = mockDocuments.findIndex(doc => doc.id === id);
    if (index !== -1) {
      mockDocuments.splice(index, 1);
      return true;
    }
    return false;
  },

  // Get processing statistics
  getProcessingStats: async (): Promise<ProcessingStats> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    return mockStats;
  },

  // Process document (mock)
  processDocument: async (id: string): Promise<Document> => {
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    const doc = mockDocuments.find(d => d.id === id);
    if (doc) {
      doc.status = 'processed';
      doc.processedDate = new Date().toISOString().split('T')[0];
      doc.confidence = Math.floor(Math.random() * 10) + 90; // 90-99%
      doc.extractedData = {
        placeholder: 'Extracted data would appear here'
      };
    }
    return doc!;
  },

  // Search documents
  searchDocuments: async (query: string): Promise<Document[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockDocuments.filter(doc => 
      doc.filename.toLowerCase().includes(query.toLowerCase()) ||
      doc.type.toLowerCase().includes(query.toLowerCase())
    );
  }
};
