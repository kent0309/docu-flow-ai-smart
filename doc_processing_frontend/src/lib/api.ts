// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Document interface matching the backend model
export interface Document {
  id: string;
  filename: string;
  document_type: string;
  status: 'processed' | 'processing' | 'error';
  uploaded_at: string;
  extracted_data?: any;
  summary?: string;
}

// Fetch all documents from the Django API
export const fetchDocuments = async (): Promise<Document[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Transform the data to match the frontend interface
    return data.map((doc: any) => ({
      id: doc.id.toString(),
      filename: doc.filename || 'Unknown File',
      type: doc.document_type || 'unknown',
      status: doc.status || 'processing',
      date: new Date(doc.uploaded_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }),
      confidence: doc.extracted_data?.confidence_score ? 
        Math.round(doc.extracted_data.confidence_score * 100) : undefined
    }));
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

// Upload a new document
export const uploadDocument = async (file: File): Promise<Document> => {
  try {
    const formData = new FormData();
    formData.append('uploaded_file', file);
    
    const response = await fetch(`${API_BASE_URL}/documents/upload/`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      id: data.id.toString(),
      filename: data.filename || file.name,
      type: data.document_type || 'unknown',
      status: data.status || 'processing',
      date: new Date(data.uploaded_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    };
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
}; 