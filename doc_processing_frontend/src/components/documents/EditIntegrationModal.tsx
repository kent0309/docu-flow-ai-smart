import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { Loader2, Save, X } from 'lucide-react';
import { IntegrationConfiguration, updateIntegration } from '../../lib/api';
import { useToast } from '../ui/use-toast';

interface EditIntegrationModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  integration: IntegrationConfiguration | null;
  onSuccess: (updatedIntegration: IntegrationConfiguration) => void;
}

const integrationTypes = [
  { value: 'erp', label: 'ERP System' },
  { value: 'sap', label: 'SAP' },
  { value: 'salesforce', label: 'Salesforce' },
  { value: 'crm', label: 'CRM System' },
  { value: 'quickbooks', label: 'QuickBooks' },
  { value: 'accounting', label: 'Accounting System' },
  { value: 'custom_api', label: 'Custom API' },
  { value: 'webhook', label: 'Webhook' },
  { value: 'database', label: 'Database' },
  { value: 'file_system', label: 'File System' },
];

export const EditIntegrationModal: React.FC<EditIntegrationModalProps> = ({
  open,
  onOpenChange,
  integration,
  onSuccess
}) => {
  const [formData, setFormData] = useState({
    name: '',
    integration_type: '',
    endpoint_url: '',
    api_key: '',
    description: '',
    status: 'active' as 'active' | 'inactive'
  });
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (integration && open) {
      setFormData({
        name: integration.name || '',
        integration_type: integration.integration_type || '',
        endpoint_url: integration.endpoint_url || '',
        api_key: integration.api_key || '',
        description: integration.description || '',
        status: integration.status || 'active'
      });
    }
  }, [integration, open]);

  const handleSave = async () => {
    if (!integration) return;

    // Basic validation
    if (!formData.name.trim()) {
      toast({
        title: "Validation Error",
        description: "Integration name is required",
        variant: "destructive"
      });
      return;
    }

    if (!formData.integration_type) {
      toast({
        title: "Validation Error",
        description: "Integration type is required",
        variant: "destructive"
      });
      return;
    }

    if (!formData.endpoint_url.trim()) {
      toast({
        title: "Validation Error",
        description: "Endpoint URL is required",
        variant: "destructive"
      });
      return;
    }

    try {
      setSaving(true);
      const updatedIntegration = await updateIntegration(integration.id, {
        name: formData.name.trim(),
        integration_type: formData.integration_type,
        endpoint_url: formData.endpoint_url.trim(),
        api_key: formData.api_key.trim() || undefined,
        description: formData.description.trim() || undefined,
        status: formData.status
      });

      toast({
        title: "Integration Updated",
        description: `${formData.name} has been updated successfully`,
      });

      onSuccess(updatedIntegration);
      onOpenChange(false);
    } catch (error) {
      console.error('Error updating integration:', error);
      toast({
        title: "Update Failed",
        description: error instanceof Error ? error.message : "Failed to update integration",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Edit Integration Configuration</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Modify the settings for "{integration?.name}" integration
          </p>
        </DialogHeader>

        <div className="space-y-6">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Integration Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Enter integration name"
            />
          </div>

          {/* Integration Type */}
          <div className="space-y-2">
            <Label htmlFor="integration_type">Integration Type *</Label>
            <Select
              value={formData.integration_type}
              onValueChange={(value) => setFormData(prev => ({ ...prev, integration_type: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select integration type" />
              </SelectTrigger>
              <SelectContent>
                {integrationTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Endpoint URL */}
          <div className="space-y-2">
            <Label htmlFor="endpoint_url">Endpoint URL *</Label>
            <Input
              id="endpoint_url"
              value={formData.endpoint_url}
              onChange={(e) => setFormData(prev => ({ ...prev, endpoint_url: e.target.value }))}
              placeholder="https://api.example.com/webhook"
            />
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <Label htmlFor="api_key">API Key</Label>
            <Input
              id="api_key"
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData(prev => ({ ...prev, api_key: e.target.value }))}
              placeholder="Enter API key (optional)"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Enter description (optional)"
              rows={3}
            />
          </div>

          {/* Status */}
          <div className="flex items-center space-x-2">
            <Switch
              id="status"
              checked={formData.status === 'active'}
              onCheckedChange={(checked) => 
                setFormData(prev => ({ ...prev, status: checked ? 'active' : 'inactive' }))
              }
            />
            <Label htmlFor="status">
              Active {formData.status === 'active' ? '(Integration enabled)' : '(Integration disabled)'}
            </Label>
          </div>
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={handleCancel}
            disabled={saving}
          >
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}; 