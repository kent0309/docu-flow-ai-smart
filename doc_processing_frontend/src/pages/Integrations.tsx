import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import MainLayout from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/use-toast';
import { EditIntegrationModal } from '@/components/documents/EditIntegrationModal';
import {
  PlusCircle, 
  Settings, 
  Play, 
  Pause, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  Clock,
  Zap,
  Database,
  Globe,
  AlertTriangle
} from 'lucide-react';

// API functions with fallback
const fetchIntegrations = async () => {
  try {
    const response = await fetch('/api/integrations/');
    if (!response.ok) throw new Error('Failed to fetch integrations');
    return response.json();
  } catch (error) {
    // Return empty array as fallback
    console.warn('API not available, using fallback data');
    return [];
  }
};

const fetchIntegrationLogs = async (integrationId?: string) => {
  try {
    const url = integrationId 
      ? `/api/integration-logs/?integration_id=${integrationId}`
      : '/api/integration-logs/';
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch integration logs');
    return response.json();
  } catch (error) {
    // Return empty array as fallback
    console.warn('API not available, using fallback data');
    return [];
  }
};

const createIntegration = async (data: any) => {
  const response = await fetch('/api/integrations/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create integration');
  return response.json();
};

const testIntegrationConnection = async (integrationId: string) => {
  const response = await fetch(`/api/integrations/${integrationId}/test_connection/`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to test connection');
  return response.json();
};

const updateIntegration = async ({ id, data }: { id: string; data: any }) => {
  const response = await fetch(`/api/integrations/${id}/`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update integration');
  return response.json();
};

const deleteIntegration = async (id: string) => {
  const response = await fetch(`/api/integrations/${id}/`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete integration');
};

const Integrations = () => {
  const [activeTab, setActiveTab] = useState('integrations');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<any>(null);
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    integration_type: '',
    description: '',
    endpoint_url: '',
    api_key: '',
    username: '',
    password: '',
    config_data: {},
    supported_document_types: [],
    sync_frequency: 60
  });

  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch integrations - simplified and reliable
  const { data: integrations = [], isLoading: integrationsLoading, error: integrationsError } = useQuery({
    queryKey: ['integrations'],
    queryFn: fetchIntegrations,
    retry: 3,
    retryDelay: 1000,
  });

  // Fetch integration logs - only when needed
  const { data: logs = [], isLoading: logsLoading, error: logsError } = useQuery({
    queryKey: ['integration-logs'],
    queryFn: () => fetchIntegrationLogs(),
    enabled: activeTab === 'logs',
    retry: 3,
    retryDelay: 1000,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: createIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      setIsCreateModalOpen(false);
      resetForm();
      toast({
        title: 'Success',
        description: 'Integration created successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create integration.',
        variant: 'destructive',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: updateIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      setIsEditModalOpen(false);
      setSelectedIntegration(null);
      toast({
        title: 'Success',
        description: 'Integration updated successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to update integration.',
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast({
        title: 'Success',
        description: 'Integration deleted successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete integration.',
        variant: 'destructive',
      });
    },
  });

  const testConnectionMutation = useMutation({
    mutationFn: testIntegrationConnection,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
      toast({
        title: 'Success',
        description: 'Connection test started.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to test connection.',
        variant: 'destructive',
      });
    },
  });

  const resetForm = () => {
    setNewIntegration({
      name: '',
      integration_type: '',
      description: '',
      endpoint_url: '',
      api_key: '',
      username: '',
      password: '',
      config_data: {},
      supported_document_types: [],
      sync_frequency: 60
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(newIntegration);
  };

  const handleEdit = (integration: any) => {
    setSelectedIntegration(integration);
    setIsEditModalOpen(true);
  };

  const handleEditSuccess = (updatedIntegration: any) => {
    queryClient.invalidateQueries({ queryKey: ['integrations'] });
    setIsEditModalOpen(false);
    setSelectedIntegration(null);
    toast({
      title: 'Integration Updated',
      description: `${updatedIntegration.name} has been updated successfully.`,
    });
  };

  const handleDelete = (integration: any) => {
    if (confirm('Are you sure you want to delete this integration?')) {
      deleteMutation.mutate(integration.id);
    }
  };

  const handleTestConnection = (integration: any) => {
    testConnectionMutation.mutate(integration.id);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'testing':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Pause className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variant = status === 'active' ? 'default' : 
                   status === 'error' ? 'destructive' : 
                   status === 'testing' ? 'secondary' : 'outline';
    
    return (
      <Badge variant={variant} className="flex items-center gap-1">
        {getStatusIcon(status)}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getIntegrationTypeIcon = (type: string) => {
    switch (type) {
      case 'sap_erp':
      case 'ms_dynamics':
        return <Database className="h-5 w-5 text-blue-500" />;
      case 'salesforce':
        return <Zap className="h-5 w-5 text-cyan-500" />;
      case 'quickbooks':
        return <Database className="h-5 w-5 text-green-500" />;
      case 'custom_api':
      case 'webhook':
        return <Globe className="h-5 w-5 text-purple-500" />;
      default:
        return <Settings className="h-5 w-5 text-gray-500" />;
    }
  };

  const getLogStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
    }
  };

  // Loading skeleton component
  const IntegrationSkeleton = () => (
    <div className="grid gap-6 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Card key={i} className="relative">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Skeleton className="h-6 w-6 rounded" />
                <div>
                  <Skeleton className="h-5 w-32 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </div>
              </div>
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex items-center gap-2 pt-2">
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-16" />
              <Skeleton className="h-8 w-20" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  // Table skeleton component
  const TableSkeleton = () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Integration</TableHead>
          <TableHead>Action</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Duration</TableHead>
          <TableHead>Started At</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3, 4, 5].map((i) => (
          <TableRow key={i}>
            <TableCell><Skeleton className="h-4 w-24" /></TableCell>
            <TableCell><Skeleton className="h-4 w-20" /></TableCell>
            <TableCell><Skeleton className="h-4 w-16" /></TableCell>
            <TableCell><Skeleton className="h-4 w-12" /></TableCell>
            <TableCell><Skeleton className="h-4 w-32" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );

  // Handle tab change
  const handleTabChange = (value: string) => {
    setActiveTab(value);
  };

  // Error handling
  if (integrationsError) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Error loading integrations</h3>
            <p className="text-muted-foreground mb-4">
              {integrationsError.message || 'Failed to load integrations'}
            </p>
            <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['integrations'] })}>
              Try Again
            </Button>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
            <p className="text-muted-foreground">
              Manage connections to external systems and monitor data synchronization
            </p>
          </div>
          <Button onClick={() => setIsCreateModalOpen(true)}>
            <PlusCircle className="h-4 w-4 mr-2" />
            Add Integration
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <TabsList>
            <TabsTrigger value="integrations">Active Integrations</TabsTrigger>
            <TabsTrigger value="logs">Activity Logs</TabsTrigger>
          </TabsList>

          <TabsContent value="integrations" className="pt-6">
            {integrationsLoading ? (
              <IntegrationSkeleton />
            ) : (
              <div className="grid gap-6 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
                {integrations.map((integration: any) => (
                  <Card key={integration.id} className="relative">
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          {getIntegrationTypeIcon(integration.integration_type)}
                          <div>
                            <CardTitle className="text-lg">{integration.name}</CardTitle>
                            <CardDescription className="text-sm">
                              {integration.integration_type.replace('_', ' ').toUpperCase()}
                            </CardDescription>
                          </div>
                        </div>
                        {getStatusBadge(integration.status)}
                      </div>
                    </CardHeader>
                    
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {integration.description || 'No description provided'}
                      </p>
                      
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Sync Frequency:</span>
                        <span>{integration.sync_frequency} min</span>
                      </div>
                      
                      {integration.last_sync && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Last Sync:</span>
                          <span>{new Date(integration.last_sync).toLocaleString()}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 pt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleTestConnection(integration)}
                          disabled={testConnectionMutation.isPending}
                        >
                          <Play className="h-3 w-3 mr-1" />
                          Test
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(integration)}
                        >
                          <Settings className="h-3 w-3 mr-1" />
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDelete(integration)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {integrations.length === 0 && (
                  <div className="col-span-full text-center py-12">
                    <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No integrations found</h3>
                    <p className="text-muted-foreground mb-4">
                      Get started by creating your first integration.
                    </p>
                    <Button onClick={() => setIsCreateModalOpen(true)}>
                      <PlusCircle className="h-4 w-4 mr-2" />
                      Add Integration
                    </Button>
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="logs" className="pt-6">
            <Card>
              <CardHeader>
                <CardTitle>Integration Activity Logs</CardTitle>
                <CardDescription>
                  Monitor integration activity and troubleshoot issues
                </CardDescription>
              </CardHeader>
              <CardContent>
                {logsLoading ? (
                  <TableSkeleton />
                ) : logsError ? (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-4" />
                    <p className="text-muted-foreground mb-4">
                      {logsError.message || 'Failed to load activity logs'}
                    </p>
                    <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['integration-logs'] })}>
                      Try Again
                    </Button>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Integration</TableHead>
                        <TableHead>Action</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Duration</TableHead>
                        <TableHead>Started At</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {logs.map((log: any) => (
                        <TableRow key={log.id}>
                          <TableCell className="font-medium">
                            {log.integration_name}
                          </TableCell>
                          <TableCell>{log.action}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getLogStatusIcon(log.status)}
                              {log.status}
                            </div>
                          </TableCell>
                          <TableCell>
                            {log.duration_ms ? `${log.duration_ms}ms` : '-'}
                          </TableCell>
                          <TableCell>
                            {new Date(log.started_at).toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
                
                {!logsLoading && !logsError && logs.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">No activity logs found.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Create Integration Modal */}
        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create New Integration</DialogTitle>
              <DialogDescription>
                Configure a new external system integration.
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Integration Name</Label>
                  <Input
                    id="name"
                    value={newIntegration.name}
                    onChange={(e) => setNewIntegration({ ...newIntegration, name: e.target.value })}
                    placeholder="e.g., SAP Production"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="type">Integration Type</Label>
                  <Select
                    value={newIntegration.integration_type}
                    onValueChange={(value) => setNewIntegration({ ...newIntegration, integration_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sap_erp">SAP ERP</SelectItem>
                      <SelectItem value="salesforce">Salesforce</SelectItem>
                      <SelectItem value="ms_dynamics">Microsoft Dynamics</SelectItem>
                      <SelectItem value="quickbooks">QuickBooks</SelectItem>
                      <SelectItem value="custom_api">Custom API</SelectItem>
                      <SelectItem value="webhook">Webhook</SelectItem>
                      <SelectItem value="database">Database</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={newIntegration.description}
                  onChange={(e) => setNewIntegration({ ...newIntegration, description: e.target.value })}
                  placeholder="Describe this integration..."
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="endpoint_url">Endpoint URL</Label>
                <Input
                  id="endpoint_url"
                  type="url"
                  value={newIntegration.endpoint_url}
                  onChange={(e) => setNewIntegration({ ...newIntegration, endpoint_url: e.target.value })}
                  placeholder="https://api.example.com"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="api_key">API Key</Label>
                  <Input
                    id="api_key"
                    type="password"
                    value={newIntegration.api_key}
                    onChange={(e) => setNewIntegration({ ...newIntegration, api_key: e.target.value })}
                    placeholder="Enter API key"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="sync_frequency">Sync Frequency (minutes)</Label>
                  <Input
                    id="sync_frequency"
                    type="number"
                    min="1"
                    value={newIntegration.sync_frequency}
                    onChange={(e) => setNewIntegration({ ...newIntegration, sync_frequency: parseInt(e.target.value) || 60 })}
                  />
                </div>
              </div>
              
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? 'Creating...' : 'Create Integration'}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>

        {/* Edit Integration Modal */}
        <EditIntegrationModal
          open={isEditModalOpen}
          onOpenChange={setIsEditModalOpen}
          integration={selectedIntegration}
          onSuccess={handleEditSuccess}
        />
      </div>
    </MainLayout>
  );
};

export default Integrations; 