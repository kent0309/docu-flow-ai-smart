
import { API_ENDPOINTS, checkBackendAvailability } from '@/config/api';

// Document interface
interface Document {
  id: string;
  title: string;
  file?: File;
  file_type?: string;
  uploaded_at?: string;
  file_name?: string;
}

// Document extraction result interface
interface ExtractionResult {
  id: string;
  status: string;
  extracted_data: any;
}

// Document summary interface
interface SummaryResult {
  id: string;
  status: string;
  summary: string;
}

export const DocumentService = {
  async uploadDocument(file: File, title: string): Promise<Document> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      
      const response = await fetch(API_ENDPOINTS.DOCUMENTS, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response for development/demo
      console.log('Using mock upload response (backend unavailable)');
      return {
        id: Math.random().toString(36).substring(2, 15),
        title,
        file_type: file.name.split('.').pop()?.toLowerCase(),
        uploaded_at: new Date().toISOString(),
        file_name: file.name
      };
    }
  },
  
  async getDocuments(): Promise<Document[]> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const response = await fetch(API_ENDPOINTS.DOCUMENTS);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch documents with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response
      console.log('Using mock documents response (backend unavailable)');
      return [];
    }
  },
  
  async extractData(documentId: string): Promise<ExtractionResult> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const response = await fetch(API_ENDPOINTS.DOCUMENT_EXTRACT(documentId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Data extraction failed with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response
      console.log('Using mock extraction response (backend unavailable)');
      return {
        id: documentId,
        status: 'completed',
        extracted_data: {
          documentType: 'Invoice',
          confidence: 95.5,
          fields: [
            { name: 'Invoice Number', value: 'INV-12345', confidence: 98, isValid: true },
            { name: 'Date', value: 'May 10, 2025', confidence: 94, isValid: true },
            { name: 'Amount Due', value: '$2,456.78', confidence: 92, isValid: true },
            { name: 'Vendor', value: 'ABC Supplies Inc.', confidence: 89, isValid: true }
          ]
        }
      };
    }
  },
  
  async summarizeDocument(documentId: string): Promise<SummaryResult> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const response = await fetch(API_ENDPOINTS.DOCUMENT_SUMMARIZE(documentId), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Summarization failed with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response
      console.log('Using mock summary response (backend unavailable)');
      return {
        id: documentId,
        status: 'completed',
        summary: 'Executive Summary:\n\nThis document discusses key financial metrics for Q3 2023, highlighting a 15% increase in revenue compared to Q2. Major points include:\n\n• Revenue growth primarily driven by expansion in Asian markets\n• Operating costs reduced by 8% due to automation initiatives\n• New product line exceeded sales targets by 22%\n• Customer retention improved to 94% (up from 89%)\n\nThe document recommends continued investment in automation and expansion of the product line to additional markets in Q4.'
      };
    }
  }
};
