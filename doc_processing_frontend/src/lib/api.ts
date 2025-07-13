// API configuration
const API_BASE_URL = 'http://localhost:8000/api';

// Document interface matching the backend model
export interface Document {
  id: string;
  filename: string;
  document_type: string;
  type?: string;
  detected_language?: string;
  status: 'processed' | 'processing' | 'error';
  uploaded_at: string;
  date?: string;
  confidence?: number;
  extracted_data?: any;
  summary?: string;
  document_subtype?: string;
}

// Integration interfaces
export interface IntegrationConfiguration {
  id: string;
  name: string;
  integration_type: string;
  endpoint_url: string;
  status: 'active' | 'inactive';
  description?: string;
  api_key?: string;
  created_at: string;
}

export interface IntegrationAuditLog {
  id: string;
  document: string;
  integration_config: IntegrationConfiguration;
  status: 'pending' | 'success' | 'failed';
  started_at: string;
  completed_at?: string;
  error_message?: string;
  response_data?: any;
}

// Workflow interfaces
export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  step_order: number;
  workflow: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  steps: WorkflowStep[];
}

export interface WorkflowTemplate {
  name: string;
  description: string;
  steps: {
    name: string;
    description: string;
    order: number;
  }[];
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
      document_type: doc.document_type || 'unknown',
      type: doc.document_type || 'other',
      detected_language: doc.detected_language,
      status: doc.status || 'processing',
      uploaded_at: doc.uploaded_at,
      date: new Date(doc.uploaded_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }),
      confidence: doc.extracted_data?.confidence_score ? 
        Math.round(doc.extracted_data.confidence_score * 100) : undefined,
      summary: doc.summary,
      // Include subtype if present
      ...(doc.extracted_data?.document_subtype && { 
        document_subtype: doc.extracted_data.document_subtype
      })
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
      document_type: data.document_type || 'unknown',
      type: data.document_type || 'other',
      detected_language: data.detected_language,
      status: data.status || 'processing',
      uploaded_at: data.uploaded_at,
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

// Get document details
export const getDocument = async (id: string): Promise<Document> => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${id}/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const doc = await response.json();

    // Handle document type from extracted data if available
    let document_type = doc.document_type || 'unknown';
    // If subtype is email, override main type
    if (doc.extracted_data?.document_subtype === 'email') {
      document_type = 'email';
    }
    
    return {
      id: doc.id.toString(),
      filename: doc.filename,
      document_type,
      type: document_type,
      detected_language: doc.detected_language,
      status: doc.status,
      uploaded_at: doc.uploaded_at,
      extracted_data: doc.extracted_data,
      summary: doc.summary,
      date: new Date(doc.uploaded_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      }),
      // Include subtype if present
      ...(doc.extracted_data?.document_subtype && { 
        document_subtype: doc.extracted_data.document_subtype
      })
    };
  } catch (error) {
    console.error(`Error fetching document ${id}:`, error);
    throw error;
  }
};

// Download extracted data in specific format
export const downloadExtractedData = async (id: string, format: 'json' | 'csv' | 'xml' = 'json') => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${id}/download_extracted_data/?format=${format}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.text();
  } catch (error) {
    console.error(`Error downloading extracted data for document ${id}:`, error);
    throw error;
  }
};

// Trigger semantic analysis
export const performSemanticAnalysis = async (id: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${id}/semantic_analysis/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error performing semantic analysis for document ${id}:`, error);
    throw error;
  }
};

// Integration-related functions

// Fetch all integration configurations
export const fetchIntegrations = async (): Promise<IntegrationConfiguration[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/integrations/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching integrations:', error);
    throw error;
  }
};

// Send document for integration
export const sendForIntegration = async (documentId: string, integrationId: string): Promise<IntegrationAuditLog> => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/send_for_integration/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        integration_id: integrationId
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error sending document ${documentId} for integration:`, error);
    throw error;
  }
};

// Update integration configuration
export const updateIntegration = async (integrationId: string, updates: Partial<IntegrationConfiguration>): Promise<IntegrationConfiguration> => {
  try {
    const response = await fetch(`${API_BASE_URL}/integrations/${integrationId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error updating integration ${integrationId}:`, error);
    throw error;
  }
};

// Test integration connection
export const testIntegrationConnection = async (integrationId: string): Promise<{ success: boolean; message?: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/integrations/${integrationId}/test_connection/`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error testing integration connection:`, error);
    throw error;
  }
};

// Fetch integration audit logs
export const fetchIntegrationLogs = async (): Promise<IntegrationAuditLog[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/integration-logs/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching integration logs:', error);
    throw error;
  }
};

// Process document through workflow
export const processDocumentWorkflow = async (documentId: string, workflowId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents/${documentId}/process_workflow/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ workflow_id: workflowId }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error processing document ${documentId} with workflow ${workflowId}:`, error);
    throw error;
  }
};

// Fetch all workflows
export const fetchWorkflows = async (): Promise<Workflow[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching workflows:', error);
    throw error;
  }
};

// Get workflow details
export const getWorkflow = async (id: string): Promise<Workflow> => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/${id}/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching workflow ${id}:`, error);
    throw error;
  }
};

// Create a new workflow
export const createWorkflow = async (workflow: Partial<Workflow>): Promise<Workflow> => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workflow),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating workflow:', error);
    throw error;
  }
};

// Get workflow templates
export const getWorkflowTemplates = async (): Promise<WorkflowTemplate[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/templates/`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching workflow templates:', error);
    throw error;
  }
};

// Create workflow from template
export const createWorkflowFromTemplate = async (templateName: string): Promise<Workflow> => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflows/create_from_template/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ template_name: templateName }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error creating workflow from template "${templateName}":`, error);
    throw error;
  }
};

// Create workflow step
export const createWorkflowStep = async (workflowStep: {
  workflow: string;
  name: string;
  description: string;
  step_order: number;
}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/workflow-steps/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workflowStep),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating workflow step:', error);
    throw error;
  }
}; 