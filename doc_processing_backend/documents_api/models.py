import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=[('processing', 'Processing'), ('processed', 'Processed'), ('error', 'Error')], default='processing')
    document_type = models.CharField(max_length=50, null=True, blank=True)
    detected_language = models.CharField(max_length=10, null=True, blank=True)
    extracted_data = models.JSONField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Add workflow status tracking
    workflow_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_review', 'In Review'),
    ], null=True, blank=True)
    current_approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pending_approvals')
    
    def __str__(self):
        return self.filename

class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add approval routing configuration
    requires_approval = models.BooleanField(default=False)
    approval_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                           help_text="Amount threshold that requires approval")
    auto_approve_below_threshold = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    STEP_TYPE_CHOICES = [
        ('processing', 'Processing'),
        ('approval', 'Approval'),
        ('integration', 'Integration'),
        ('notification', 'Notification'),
    ]
    
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    step_order = models.PositiveIntegerField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPE_CHOICES, default='processing')
    
    # Approval step configuration
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_steps')
    approval_group = models.CharField(max_length=100, blank=True, null=True, help_text="Group of users who can approve")
    requires_all_approvers = models.BooleanField(default=False)
    
    # Integration step configuration
    integration_system = models.CharField(max_length=100, blank=True, null=True)
    integration_config = models.JSONField(blank=True, null=True)
    
    # Conditional step execution
    condition_field = models.CharField(max_length=100, blank=True, null=True)
    condition_value = models.CharField(max_length=255, blank=True, null=True)
    condition_operator = models.CharField(max_length=10, choices=[
        ('eq', 'Equals'),
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('contains', 'Contains'),
    ], blank=True, null=True)

    class Meta:
        ordering = ['step_order']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.step_order}: {self.name}"

class Notification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    workflow = models.ForeignKey(Workflow, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Notification to {self.recipient_email}: {self.subject}"

class ValidationRule(models.Model):
    RULE_TYPE_CHOICES = [
        ('regex', 'Regular Expression'),
        ('data_type', 'Data Type'),
        ('required', 'Required Field'),
        ('range', 'Value Range'),
        ('enum', 'Enumeration'),
        ('cross_reference', 'Cross-Reference Validation'),
        ('calculation', 'Calculation Validation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    rule_pattern = models.CharField(max_length=255, help_text="Regex pattern, data type name, or other validation criteria")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for cross-reference and calculation validation
    reference_field = models.CharField(max_length=100, blank=True, null=True, help_text="Field to compare against (e.g., 'items' for line items)")
    calculation_type = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('sum', 'Sum'),
        ('average', 'Average'),
        ('count', 'Count'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ], help_text="Type of calculation for cross-reference validation")
    tolerance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Acceptable difference for numerical comparisons")
    auto_created = models.BooleanField(default=False, help_text="Whether this rule was automatically created from patterns")
    
    def __str__(self):
        return f"{self.name} ({self.document_type} - {self.field_name})"

# New models for integration and advanced routing

class IntegrationConfiguration(models.Model):
    INTEGRATION_TYPE_CHOICES = [
        ('sap_erp', 'SAP ERP'),
        ('salesforce', 'Salesforce'),
        ('ms_dynamics', 'Microsoft Dynamics'),
        ('quickbooks', 'QuickBooks'),
        ('custom_api', 'Custom API'),
        ('webhook', 'Webhook'),
        ('database', 'Database'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('testing', 'Testing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Connection configuration
    endpoint_url = models.URLField(max_length=500, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)  # Should be encrypted in production
    
    # Configuration settings
    config_data = models.JSONField(default=dict, help_text="Additional configuration parameters")
    supported_document_types = models.JSONField(default=list, help_text="List of supported document types")
    
    # Status and monitoring
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_frequency = models.PositiveIntegerField(default=60, help_text="Sync frequency in minutes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.integration_type})"

class IntegrationAuditLog(models.Model):
    ACTION_CHOICES = [
        ('sync', 'Synchronization'),
        ('send', 'Data Send'),
        ('receive', 'Data Receive'),
        ('error', 'Error'),
        ('test', 'Test Connection'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(IntegrationConfiguration, on_delete=models.CASCADE, related_name='audit_logs')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True, related_name='integration_logs')
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Request/Response data
    request_data = models.JSONField(blank=True, null=True)
    response_data = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timing information
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    
    # External system reference
    external_reference_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.integration.name} - {self.action} - {self.status}"

class DocumentApproval(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='approvals')
    workflow_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='approvals')
    
    # Approval details
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_approvals')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True)
    
    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Delegation
    delegated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delegated_approvals')
    delegation_reason = models.TextField(blank=True, null=True)
    
    # Approval level (for multi-level approvals)
    approval_level = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.document.filename} - {self.approver.username} - {self.status}"

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='workflow_executions')
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    current_step = models.ForeignKey(WorkflowStep, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Execution details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Execution data
    execution_data = models.JSONField(default=dict, help_text="Data collected during workflow execution")
    error_log = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.document.filename} - {self.workflow.name} - {self.status}"

class RealTimeSyncStatus(models.Model):
    SYNC_TYPE_CHOICES = [
        ('document_status', 'Document Status'),
        ('approval_status', 'Approval Status'),
        ('integration_data', 'Integration Data'),
        ('workflow_progress', 'Workflow Progress'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='sync_statuses')
    integration = models.ForeignKey(IntegrationConfiguration, on_delete=models.CASCADE, related_name='sync_statuses')
    
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    last_sync = models.DateTimeField(auto_now=True)
    next_sync = models.DateTimeField(null=True, blank=True)
    
    # Sync status
    is_synced = models.BooleanField(default=False)
    sync_error = models.TextField(blank=True, null=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # External system data
    external_id = models.CharField(max_length=255, blank=True, null=True)
    external_status = models.CharField(max_length=100, blank=True, null=True)
    external_data = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.document.filename} - {self.integration.name} - {self.sync_type}"
