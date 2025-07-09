from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, WorkflowViewSet, WorkflowStepViewSet, ValidationRuleViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)
router.register(r'workflows', WorkflowViewSet)
router.register(r'workflow-steps', WorkflowStepViewSet)
router.register(r'validation-rules', ValidationRuleViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 