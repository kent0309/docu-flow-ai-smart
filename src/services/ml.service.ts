
import { API_ENDPOINTS, checkBackendAvailability, getCommonHeaders } from '@/config/api';

export interface ModelStats {
  status: string;
  documentTypes: string[];
  totalDocumentsProcessed: number;
  accuracy: number;
  lastTrainingDate: string;
  confidenceByDocType: Record<string, number>;
  mediaDirectory?: string;
  modelExists?: boolean;
}

export interface TrainingResult {
  status: string;
  message: string;
}

export const MLService = {
  async trainModel(): Promise<TrainingResult> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const response = await fetch(API_ENDPOINTS.ML_TRAIN, {
        method: 'POST',
        headers: getCommonHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`Model training failed with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response
      console.log('Using mock training response (backend unavailable)');
      return {
        status: 'success',
        message: 'Model training completed successfully (simulated)'
      };
    }
  },
  
  async getModelStats(): Promise<ModelStats> {
    const isBackendAvailable = await checkBackendAvailability();
    
    if (isBackendAvailable) {
      const response = await fetch(API_ENDPOINTS.ML_STATS, {
        headers: getCommonHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch model stats with status: ${response.status}`);
      }
      
      return await response.json();
    } else {
      // Mock response
      console.log('Using mock model stats response (backend unavailable)');
      return {
        status: 'active',
        documentTypes: ['Invoice', 'Financial Report', 'Contract', 'Receipt', 'General Document'],
        totalDocumentsProcessed: 157,
        accuracy: 92.5,
        lastTrainingDate: '2025-05-01T14:32:45Z',
        confidenceByDocType: {
          'Invoice': 96.3,
          'Financial Report': 94.1,
          'Contract': 89.7,
          'Receipt': 91.5,
          'General Document': 83.2
        }
      };
    }
  }
};
