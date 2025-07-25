from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, WorkflowViewSet, WorkflowStepViewSet, 
    ValidationRuleViewSet, NotificationViewSet,
    IntegrationConfigurationViewSet, IntegrationAuditLogViewSet,
    DocumentApprovalViewSet, WorkflowExecutionViewSet, RealTimeSyncStatusViewSet,
    BusinessRulesViewSet,
    download_document_data,  # Import the direct view function
    test_endpoint,  # Add test endpoint
    download_document_csv  # Add CSV download function
)

# Configure router with explicit trailing slash handling
router = DefaultRouter(trailing_slash=True)
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'workflow-steps', WorkflowStepViewSet, basename='workflowstep')
router.register(r'validation-rules', ValidationRuleViewSet, basename='validationrule')
router.register(r'notifications', NotificationViewSet, basename='notification')

# New endpoints for enhanced features
router.register(r'integrations', IntegrationConfigurationViewSet, basename='integration')
router.register(r'integration-logs', IntegrationAuditLogViewSet, basename='integration-log')
router.register(r'approvals', DocumentApprovalViewSet, basename='approval')
router.register(r'workflow-executions', WorkflowExecutionViewSet, basename='workflow-execution')
router.register(r'sync-status', RealTimeSyncStatusViewSet, basename='sync-status')
router.register(r'business-rules', BusinessRulesViewSet, basename='business-rules')

# Create document viewset actions manually
document_list = DocumentViewSet.as_view({'get': 'list', 'post': 'create'})
document_detail = DocumentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update', 
    'patch': 'partial_update',
    'delete': 'destroy'
})
document_upload = DocumentViewSet.as_view({'post': 'upload'})
document_test = DocumentViewSet.as_view({'get': 'test_action'})
document_semantic = DocumentViewSet.as_view({'get': 'semantic_analysis'})
document_workflow = DocumentViewSet.as_view({'post': 'process_workflow'})
document_validate = DocumentViewSet.as_view({'post': 'validate'})
document_validation_status = DocumentViewSet.as_view({'get': 'validation_status'})
document_trigger_workflow = DocumentViewSet.as_view({'post': 'trigger_workflow'})
document_integrate = DocumentViewSet.as_view({'post': 'integrate_with_system'})
document_integrations = DocumentViewSet.as_view({'get': 'available_integrations'})
document_with_approvals = DocumentViewSet.as_view({'get': 'with_approvals'})
document_start_sync = DocumentViewSet.as_view({'post': 'start_sync'})
document_send_to_approval = DocumentViewSet.as_view({'post': 'send_to_approval'})
document_send_for_integration = DocumentViewSet.as_view({'post': 'send_for_integration'})

urlpatterns = [
    # IMPORTANT: Static endpoints must come BEFORE parameterized ones
    
    # Static document endpoints (no parameters)
    path('documents/upload/', document_upload, name='document-upload'),
    path('documents/available_integrations/', document_integrations, name='document-available-integrations'),
    
    # Document list endpoint
    path('documents/', document_list, name='document-list'),
    
    # Test endpoint for debugging
    path('test/', test_endpoint, name='test-endpoint'),
    
    # Parameterized document endpoints (with <str:pk>)
    path('documents/<str:pk>/', document_detail, name='document-detail'),
    
    # CSV download endpoint
    path('documents/<str:pk>/export-csv/', download_document_csv, name='document-export-csv'),
    
    # Download endpoints with format as URL parameter
    path('documents/<str:pk>/download_extracted_data/<str:format>/', download_document_data, name='document-download-with-format'),
    
    # Keep the original endpoint with query parameters for backward compatibility
    path('documents/<str:pk>/download_extracted_data/', download_document_data, name='document-download-data'),
    path('documents/<str:pk>/download_extracted_data', download_document_data, name='document-download-data-no-slash'),
    path('documents/<str:pk>/test_action/', document_test, name='document-test-action'),
    path('documents/<str:pk>/semantic_analysis/', document_semantic, name='document-semantic-analysis'),
    path('documents/<str:pk>/process_workflow/', document_workflow, name='document-process-workflow'),
    path('documents/<str:pk>/validate/', document_validate, name='document-validate'),
    path('documents/<str:pk>/validation_status/', document_validation_status, name='document-validation-status'),
    path('documents/<str:pk>/trigger_workflow/', document_trigger_workflow, name='document-trigger-workflow'),
    path('documents/<str:pk>/integrate_with_system/', document_integrate, name='document-integrate-with-system'),
    path('documents/<str:pk>/with_approvals/', document_with_approvals, name='document-with-approvals'),
    path('documents/<str:pk>/start_sync/', document_start_sync, name='document-start-sync'),
    path('documents/<str:pk>/send-to-approval/', document_send_to_approval, name='document-send-to-approval'),
    path('documents/<str:pk>/send-for-integration/', document_send_for_integration, name='document-send-for-integration'),
    
    # Include router URLs for other viewsets
    path('', include(router.urls)),
] 