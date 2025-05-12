
// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  // Document endpoints
  DOCUMENTS: `${API_BASE_URL}/documents/`,
  DOCUMENT_DETAIL: (id: string) => `${API_BASE_URL}/documents/${id}/`,
  DOCUMENT_SUMMARIZE: (id: string) => `${API_BASE_URL}/documents/${id}/summarize/`,
  DOCUMENT_EXTRACT: (id: string) => `${API_BASE_URL}/documents/${id}/extract/`,
  
  // Processed document endpoints
  PROCESSED_DOCUMENTS: `${API_BASE_URL}/processed-documents/`,
  PROCESSED_DOCUMENT_DETAIL: (id: string) => `${API_BASE_URL}/processed-documents/${id}/`,
  
  // ML endpoints
  ML_TRAIN: `${API_BASE_URL}/ml/train/`,
  ML_STATS: `${API_BASE_URL}/ml/stats/`,
};

// Function to check if the backend is available
export const checkBackendAvailability = async (): Promise<boolean> => {
  try {
    const response = await fetch(API_ENDPOINTS.DOCUMENTS, {
      method: 'HEAD',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 3000, // 3 second timeout
    });
    return response.ok;
  } catch (error) {
    console.warn('Backend API is not available:', error);
    return false;
  }
};

// Helper function to get a simple token for development purposes
// In a real application, this would be replaced with proper authentication
export const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Common headers for API requests
export const getCommonHeaders = () => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};
