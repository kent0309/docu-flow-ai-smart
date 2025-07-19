import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Loader2, CheckCircle, Zap, Database, Cloud, Settings, Edit } from 'lucide-react';
import { IntegrationConfiguration, fetchIntegrations, sendForIntegration } from '../../lib/api';
import { useToast } from '../ui/use-toast';
import { EditIntegrationModal } from './EditIntegrationModal';

interface IntegrationSelectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentId: string;
  documentName: string;
  onSuccess: () => void;
}

const getIntegrationIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'erp':
    case 'sap':
      return <Database className="h-5 w-5 text-blue-600" />;
    case 'salesforce':
    case 'crm':
      return <Cloud className="h-5 w-5 text-green-600" />;
    case 'quickbooks':
    case 'accounting':
      return <Settings className="h-5 w-5 text-purple-600" />;
    default:
      return <Zap className="h-5 w-5 text-orange-600" />;
  }
};

const getIntegrationTypeColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'erp':
    case 'sap':
      return 'bg-blue-100 text-blue-800';
    case 'salesforce':
    case 'crm':
      return 'bg-green-100 text-green-800';
    case 'quickbooks':
    case 'accounting':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-orange-100 text-orange-800';
  }
};

export const IntegrationSelectionDialog: React.FC<IntegrationSelectionDialogProps> = ({
  open,
  onOpenChange,
  documentId,
  documentName,
  onSuccess
}) => {
  const [integrations, setIntegrations] = useState<IntegrationConfiguration[]>([]);
  const [selectedIntegration, setSelectedIntegration] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [editingIntegration, setEditingIntegration] = useState<IntegrationConfiguration | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      loadIntegrations();
    }
  }, [open]);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const data = await fetchIntegrations();
      // Only show active integrations
      const activeIntegrations = data.filter(integration => integration.status === 'active');
      setIntegrations(activeIntegrations);
    } catch (error) {
      console.error('Error loading integrations:', error);
      toast({
        title: "Error",
        description: "Failed to load integration configurations",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditIntegration = (integration: IntegrationConfiguration) => {
    setEditingIntegration(integration);
    setShowEditModal(true);
  };

  const handleEditSuccess = (updatedIntegration: IntegrationConfiguration) => {
    // Update the integration in the list
    setIntegrations(prev => 
      prev.map(integration => 
        integration.id === updatedIntegration.id ? updatedIntegration : integration
      )
    );
    
    toast({
      title: "Integration Updated",
      description: `${updatedIntegration.name} has been updated successfully`,
    });
  };

  const handleSendForIntegration = async () => {
    if (!selectedIntegration) {
      toast({
        title: "No Integration Selected",
        description: "Please select an integration system first",
        variant: "destructive"
      });
      return;
    }

    try {
      setSending(true);
      const result = await sendForIntegration(documentId, selectedIntegration);
      
      // Find the selected integration details for the success message
      const selectedIntegrationDetails = integrations.find(integration => integration.id === selectedIntegration);
      const systemName = selectedIntegrationDetails?.name || 'external system';
      
      toast({
        title: "Integration Sent Successfully",
        description: `Successfully sent ${documentName} to ${systemName}`,
      });
      
      onSuccess();
      onOpenChange(false);
    } catch (error) {
      console.error('Error sending for integration:', error);
      toast({
        title: "Integration Failed",
        description: error instanceof Error ? error.message : "Failed to send document for integration",
        variant: "destructive"
      });
    } finally {
      setSending(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Select Integration System</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Choose which external system to send "{documentName}" to for processing
          </p>
        </DialogHeader>

        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Loading integrations...</span>
            </div>
          ) : integrations.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No active integrations found</p>
              <p className="text-sm">Contact your administrator to set up integrations</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {integrations.map((integration) => (
                <Card 
                  key={integration.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    selectedIntegration === integration.id 
                      ? 'ring-2 ring-primary bg-primary/5' 
                      : ''
                  }`}
                  onClick={() => setSelectedIntegration(integration.id)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getIntegrationIcon(integration.integration_type)}
                        <div>
                          <CardTitle className="text-lg">{integration.name}</CardTitle>
                          <Badge 
                            variant="secondary" 
                            className={getIntegrationTypeColor(integration.integration_type)}
                          >
                            {integration.integration_type.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      {selectedIntegration === integration.id && (
                        <CheckCircle className="h-5 w-5 text-primary" />
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {integration.description && (
                        <p className="text-sm text-muted-foreground">
                          {integration.description}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">
                          Endpoint: {integration.endpoint_url}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditIntegration(integration);
                          }}
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={() => onOpenChange(false)}
            disabled={sending}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSendForIntegration}
            disabled={!selectedIntegration || sending}
          >
            {sending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Sending...
              </>
            ) : (
              'Send for Integration'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
      
      {/* Edit Integration Modal */}
      <EditIntegrationModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        integration={editingIntegration}
        onSuccess={handleEditSuccess}
      />
    </Dialog>
  );
}; 