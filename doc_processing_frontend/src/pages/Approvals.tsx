import React, { useState, useEffect } from 'react';
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
import {
  CheckCircle,
  XCircle,
  Clock,
  Users,
  FileText,
  AlertCircle,
  ChevronRight,
  Eye,
  MessageCircle,
  Send,
  RefreshCw
} from 'lucide-react';

// API functions
const fetchApprovals = async (filters?: any) => {
  try {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.my_approvals) params.append('my_approvals', 'true');
    
    const url = `/api/approvals/?${params}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch approvals: ${response.status}`);
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('Error fetching approvals:', error);
    throw error;
  }
};

const approveDocument = async ({ id, comments }: { id: string; comments?: string }) => {
  const response = await fetch(`/api/approvals/${id}/approve/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ comments }),
  });
  if (!response.ok) throw new Error('Failed to approve document');
  return response.json();
};

const rejectDocument = async ({ id, comments }: { id: string; comments?: string }) => {
  const response = await fetch(`/api/approvals/${id}/reject/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ comments }),
  });
  if (!response.ok) throw new Error('Failed to reject document');
  return response.json();
};

const removeApproval = async ({ id }: { id: string }) => {
  const response = await fetch(`/api/approvals/${id}/`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!response.ok) throw new Error('Failed to remove approval');
  return response.json();
};

const Approvals = () => {
  const [selectedTab, setSelectedTab] = useState('pending');
  const [selectedApproval, setSelectedApproval] = useState<any>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [actionType, setActionType] = useState<'approve' | 'reject' | 'remove'>('approve');
  const [comments, setComments] = useState('');

  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Fetch approvals
  const { data: approvals = [], isLoading: approvalsLoading, error: approvalsError, refetch: refetchApprovals } = useQuery({
    queryKey: ['approvals', selectedTab],
    queryFn: () => fetchApprovals({ 
      status: selectedTab === 'pending' ? 'pending' : selectedTab === 'approved' ? 'approved' : selectedTab,
      my_approvals: true 
    }),
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 5000,
    refetchInterval: 30000,
  });

  // Mutations
  const approveMutation = useMutation({
    mutationFn: approveDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      setIsActionModalOpen(false);
      setComments('');
      toast({
        title: 'Success',
        description: 'Document approved successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to approve document.',
        variant: 'destructive',
      });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: rejectDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      setIsActionModalOpen(false);
      setComments('');
      toast({
        title: 'Success',
        description: 'Document rejected successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to reject document.',
        variant: 'destructive',
      });
    },
  });

  const removeMutation = useMutation({
    mutationFn: removeApproval,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
      setIsActionModalOpen(false);
      toast({
        title: 'Success',
        description: 'Approval removed successfully.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to remove approval.',
        variant: 'destructive',
      });
    },
  });

  const handleAction = (approval: any, action: 'approve' | 'reject' | 'remove') => {
    setSelectedApproval(approval);
    setActionType(action);
    setIsActionModalOpen(true);
  };

  const handleSubmitAction = () => {
    if (!selectedApproval) return;

    if (actionType === 'approve') {
      approveMutation.mutate({ id: selectedApproval.id, comments });
    } else if (actionType === 'reject') {
      rejectMutation.mutate({ id: selectedApproval.id, comments });
    } else if (actionType === 'remove') {
      removeMutation.mutate({ id: selectedApproval.id });
    }
  };

  const viewDocumentDetails = (approval: any) => {
    setSelectedApproval(approval);
    setIsDetailsModalOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const statusStyles = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      approved: 'bg-green-100 text-green-800 border-green-200',
      rejected: 'bg-red-100 text-red-800 border-red-200',
    };

    const statusIcons = {
      pending: Clock,
      approved: CheckCircle,
      rejected: XCircle,
    };

    const Icon = statusIcons[status as keyof typeof statusIcons] || Clock;
    const className = statusStyles[status as keyof typeof statusStyles] || statusStyles.pending;

    return (
      <Badge variant="outline" className={className}>
        <Icon className="h-3 w-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getPriorityBadge = (dueDate: string) => {
    const due = new Date(dueDate);
    const now = new Date();
    const diffHours = (due.getTime() - now.getTime()) / (1000 * 60 * 60);

    if (diffHours < 0) {
      return <Badge variant="destructive">Overdue</Badge>;
    } else if (diffHours < 24) {
      return <Badge variant="outline" className="bg-orange-100 text-orange-800">Urgent</Badge>;
    } else {
      return <Badge variant="outline" className="bg-blue-100 text-blue-800">Normal</Badge>;
    }
  };

  const ApprovalSkeleton = () => (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1 space-y-3">
                <div className="flex items-center gap-3">
                  <Skeleton className="h-5 w-5" />
                  <div>
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32 mt-1" />
                  </div>
                  <Skeleton className="h-6 w-20" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-16" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const handleTabChange = (value: string) => {
    setSelectedTab(value);
  };

  // Error handling
  if (approvalsError) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-[400px]">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Error loading approvals</h3>
            <p className="text-muted-foreground mb-4">
              {approvalsError.message || 'Failed to load approvals'}
            </p>
            <div className="space-x-2">
              <Button onClick={() => refetchApprovals()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
              <Button variant="outline" onClick={() => window.location.reload()}>
                Reload Page
              </Button>
            </div>
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
            <h1 className="text-3xl font-bold tracking-tight">Approvals</h1>
            <p className="text-muted-foreground">
              Review and approve documents in your approval queue
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {approvalsLoading ? '...' : approvals.filter((a: any) => a.status === 'pending').length} Pending
            </Badge>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => refetchApprovals()}
              disabled={approvalsLoading}
            >
              <RefreshCw className={`h-4 w-4 ${approvalsLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        <Tabs value={selectedTab} onValueChange={handleTabChange} className="w-full">
          <TabsList>
            <TabsTrigger value="pending">
              Pending {approvalsLoading ? '' : `(${approvals.filter((a: any) => a.status === 'pending').length})`}
            </TabsTrigger>
            <TabsTrigger value="approved">Approved</TabsTrigger>
            <TabsTrigger value="rejected">Rejected</TabsTrigger>
          </TabsList>

          <TabsContent value={selectedTab} className="pt-6">
            {approvalsLoading ? (
              <ApprovalSkeleton />
            ) : (
              <div className="space-y-4">
                {approvals.length > 0 ? (
                  approvals.map((approval: any) => (
                    <Card key={approval.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 space-y-3">
                            <div className="flex items-center gap-3">
                              <FileText className="h-5 w-5 text-muted-foreground" />
                              <div>
                                <h3 className="font-semibold text-lg">{approval.document_filename || 'Unknown Document'}</h3>
                                <p className="text-sm text-muted-foreground">
                                  Level {approval.approval_level || 1} Approval
                                </p>
                              </div>
                              {getStatusBadge(approval.status)}
                              {approval.due_date && getPriorityBadge(approval.due_date)}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-muted-foreground">Assigned:</span>
                                <p className="font-medium">
                                  {approval.assigned_at ? new Date(approval.assigned_at).toLocaleString() : 'Unknown'}
                                </p>
                              </div>
                              {approval.due_date && (
                                <div>
                                  <span className="text-muted-foreground">Due:</span>
                                  <p className="font-medium">{new Date(approval.due_date).toLocaleString()}</p>
                                </div>
                              )}
                            </div>

                            {approval.comments && (
                              <div className="bg-muted p-3 rounded-md">
                                <div className="flex items-center gap-2 mb-1">
                                  <MessageCircle className="h-4 w-4" />
                                  <span className="text-sm font-medium">Comments:</span>
                                </div>
                                <p className="text-sm">{approval.comments}</p>
                              </div>
                            )}
                          </div>

                          <div className="flex items-center gap-2 ml-4">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => viewDocumentDetails(approval)}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View
                            </Button>

                            {approval.status === 'pending' && (
                              <>
                                <Button
                                  size="sm"
                                  onClick={() => handleAction(approval, 'approve')}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Approve
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleAction(approval, 'reject')}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Reject
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleAction(approval, 'remove')}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Remove
                                </Button>
                              </>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <CheckCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No {selectedTab} approvals</h3>
                    <p className="text-muted-foreground">
                      {selectedTab === 'pending' 
                        ? "You're all caught up! No pending approvals at the moment."
                        : `No ${selectedTab} approvals found.`
                      }
                    </p>
                    <Button 
                      variant="outline" 
                      className="mt-4" 
                      onClick={() => refetchApprovals()}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh
                    </Button>
                  </div>
                )}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Action Modal */}
        <Dialog open={isActionModalOpen} onOpenChange={setIsActionModalOpen}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>
                {actionType === 'approve' ? 'Approve Document' : 
                 actionType === 'reject' ? 'Reject Document' : 'Remove Approval'}
              </DialogTitle>
              <DialogDescription>
                {selectedApproval && (
                  <>
                    Document: {selectedApproval.document_filename}
                    {actionType === 'remove' && (
                      <div className="mt-2 text-destructive">
                        Are you sure you want to remove this approval? This action cannot be undone.
                      </div>
                    )}
                  </>
                )}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {actionType === 'remove' ? (
                <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-800">
                    This will permanently remove the approval from the system.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="comments">Comments (Optional)</Label>
                  <Textarea
                    id="comments"
                    value={comments}
                    onChange={(e) => setComments(e.target.value)}
                    placeholder={`Add comments for this ${actionType}...`}
                  />
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setIsActionModalOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSubmitAction}
                className={actionType === 'approve' ? 'bg-green-600 hover:bg-green-700' : 
                          actionType === 'reject' ? 'bg-red-600 hover:bg-red-700' : 
                          actionType === 'remove' ? 'bg-red-600 hover:bg-red-700' : ''}
                disabled={approveMutation.isPending || rejectMutation.isPending || removeMutation.isPending}
              >
                {(approveMutation.isPending || rejectMutation.isPending || removeMutation.isPending) && (
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                )}
                {actionType === 'approve' ? 'Approve' : 
                 actionType === 'reject' ? 'Reject' : 'Remove'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Details Modal */}
        <Dialog open={isDetailsModalOpen} onOpenChange={setIsDetailsModalOpen}>
          <DialogContent className="sm:max-w-[700px]">
            <DialogHeader>
              <DialogTitle>Document Details</DialogTitle>
              <DialogDescription>
                Detailed information about the document and approval process
              </DialogDescription>
            </DialogHeader>

            {selectedApproval && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Document</Label>
                    <p className="font-medium">{selectedApproval.document_filename}</p>
                  </div>
                  <div>
                    <Label>Status</Label>
                    <div className="mt-1">{getStatusBadge(selectedApproval.status)}</div>
                  </div>
                  <div>
                    <Label>Approval Level</Label>
                    <p className="font-medium">{selectedApproval.approval_level}</p>
                  </div>
                  <div>
                    <Label>Assigned Date</Label>
                    <p className="font-medium">
                      {selectedApproval.assigned_at ? new Date(selectedApproval.assigned_at).toLocaleString() : 'Unknown'}
                    </p>
                  </div>
                  {selectedApproval.due_date && (
                    <div>
                      <Label>Due Date</Label>
                      <p className="font-medium">{new Date(selectedApproval.due_date).toLocaleString()}</p>
                    </div>
                  )}
                </div>

                {selectedApproval.comments && (
                  <div>
                    <Label>Comments</Label>
                    <div className="mt-1 p-3 bg-muted rounded-md">
                      <p>{selectedApproval.comments}</p>
                    </div>
                  </div>
                )}

                <div>
                  <Label>Approver</Label>
                  <p className="font-medium">
                    {selectedApproval.approver ? 
                      `${selectedApproval.approver.username} (${selectedApproval.approver.email})` : 
                      'Unknown'
                    }
                  </p>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDetailsModalOpen(false)}>
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  );
};

export default Approvals; 