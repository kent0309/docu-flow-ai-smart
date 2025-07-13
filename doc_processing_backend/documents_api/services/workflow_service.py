import asyncio
import uuid
import smtplib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class AdvancedWorkflowService:
    """
    Advanced workflow service with multi-level approval routing and real-time processing
    """
    
    def __init__(self):
        self.active_workflows = {}
        self.approval_timeout = 24 * 60 * 60  # 24 hours in seconds
    
    async def start_document_workflow(self, document, workflow, started_by=None):
        """
        Start a document workflow with advanced routing capabilities
        
        Args:
            document: The document to process
            workflow: The workflow to use
            started_by: User who started the workflow
        
        Returns:
            dict: Details about the started workflow
        """
        from ..models import WorkflowExecution, WorkflowStep
        
        try:
            # Check if workflow requires approval and document meets criteria
            if workflow.requires_approval:
                approval_needed = await self._check_approval_required(document, workflow)
                if not approval_needed:
                    return await self._auto_approve_document(document, workflow)
            
            # Create workflow execution record
            execution = WorkflowExecution(
                document=document,
                workflow=workflow,
                status='started',
                started_by=started_by,
                execution_data={
                    'start_time': timezone.now().isoformat(),
                    'steps_completed': 0,
                    'total_steps': await workflow.steps.acount()
                }
            )
            await execution.asave()
            
            # Get the first step
            first_step = await workflow.steps.filter(step_order=1).afirst()
            if not first_step:
                execution.status = 'failed'
                execution.error_log = 'No steps defined in workflow'
                await execution.asave()
                return {
                    "status": "failed",
                    "error": "No steps defined in this workflow",
                    "workflow_id": str(workflow.id),
                    "workflow_name": workflow.name
                }
            
            # Update execution with current step
            execution.current_step = first_step
            execution.status = 'in_progress'
            await execution.asave()
            
            # Execute the first step
            result = await self._execute_workflow_step(execution, first_step)
            
            # Store execution in active workflows for monitoring
            self.active_workflows[str(execution.id)] = {
                'execution': execution,
                'last_activity': timezone.now(),
                'notifications_sent': []
            }
            
            return {
                "status": "started",
                "execution_id": str(execution.id),
                "document_id": str(document.id),
                "workflow_id": str(workflow.id),
                "workflow_name": workflow.name,
                "current_step": first_step.name,
                "step_result": result
            }
            
        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "workflow_id": str(workflow.id),
                "workflow_name": workflow.name
            }
    
    async def _check_approval_required(self, document, workflow):
        """
        Check if document requires approval based on workflow criteria
        """
        if not workflow.requires_approval:
            return False
        
        # Check approval threshold
        if workflow.approval_threshold:
            try:
                # Extract amount from document
                amount = await self._extract_document_amount(document)
                if amount and amount < workflow.approval_threshold:
                    if workflow.auto_approve_below_threshold:
                        return False
            except Exception:
                pass  # Continue with approval process if amount extraction fails
        
        return True
    
    async def _extract_document_amount(self, document):
        """
        Extract monetary amount from document for approval threshold check
        """
        if not document.extracted_data:
            return None
        
        # Look for common amount fields
        amount_fields = ['total', 'amount', 'total_amount', 'grand_total', 'subtotal']
        for field in amount_fields:
            if field in document.extracted_data:
                field_data = document.extracted_data[field]
                if isinstance(field_data, dict) and 'value' in field_data:
                    try:
                        return float(field_data['value'])
                    except (ValueError, TypeError):
                        continue
                elif isinstance(field_data, (int, float)):
                    return float(field_data)
        
        return None
    
    async def _auto_approve_document(self, document, workflow):
        """
        Auto-approve document when it meets auto-approval criteria
        """
        from ..models import WorkflowExecution
        
        # Create completed execution
        execution = WorkflowExecution(
            document=document,
            workflow=workflow,
            status='completed',
            execution_data={
                'auto_approved': True,
                'auto_approval_reason': 'Below threshold amount',
                'completed_at': timezone.now().isoformat()
            }
        )
        await execution.asave()
        
        # Update document status
        document.workflow_status = 'approved'
        await document.asave()
        
        return {
            "status": "auto_approved",
            "execution_id": str(execution.id),
            "document_id": str(document.id),
            "workflow_id": str(workflow.id),
            "reason": "Document auto-approved based on workflow criteria"
        }
    
    async def _execute_workflow_step(self, execution, step):
        """
        Execute a specific workflow step
        """
        try:
            # Update execution data
            execution.execution_data['current_step'] = step.name
            execution.execution_data['step_start_time'] = timezone.now().isoformat()
            await execution.asave()
            
            # Check step conditions
            if not await self._check_step_conditions(execution.document, step):
                return await self._skip_step(execution, step)
            
            # Execute step based on type
            if step.step_type == 'approval':
                return await self._execute_approval_step(execution, step)
            elif step.step_type == 'integration':
                return await self._execute_integration_step(execution, step)
            elif step.step_type == 'notification':
                return await self._execute_notification_step(execution, step)
            else:  # processing
                return await self._execute_processing_step(execution, step)
                
        except Exception as e:
            logger.error(f"Error executing step {step.name}: {str(e)}")
            execution.error_log = str(e)
            execution.status = 'failed'
            await execution.asave()
            return {"status": "failed", "error": str(e)}
    
    async def _check_step_conditions(self, document, step):
        """
        Check if step conditions are met
        """
        if not step.condition_field:
            return True
        
        # Get field value from document
        field_value = await self._get_document_field_value(document, step.condition_field)
        if field_value is None:
            return False
        
        # Check condition
        condition_value = step.condition_value
        operator = step.condition_operator
        
        if operator == 'eq':
            return str(field_value) == str(condition_value)
        elif operator == 'gt':
            try:
                return float(field_value) > float(condition_value)
            except (ValueError, TypeError):
                return False
        elif operator == 'lt':
            try:
                return float(field_value) < float(condition_value)
            except (ValueError, TypeError):
                return False
        elif operator == 'contains':
            return str(condition_value).lower() in str(field_value).lower()
        
        return False
    
    async def _get_document_field_value(self, document, field_name):
        """
        Get field value from document extracted data
        """
        if not document.extracted_data:
            return None
        
        # Handle nested field names
        if '.' in field_name:
            keys = field_name.split('.')
            value = document.extracted_data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
        else:
            value = document.extracted_data.get(field_name)
        
        # Extract value from confidence structure
        if isinstance(value, dict) and 'value' in value:
            return value['value']
        
        return value
    
    async def _skip_step(self, execution, step):
        """
        Skip a step that doesn't meet conditions
        """
        execution.execution_data['steps_skipped'] = execution.execution_data.get('steps_skipped', 0) + 1
        execution.execution_data['skip_reason'] = f"Step {step.name} conditions not met"
        await execution.asave()
        
        # Move to next step
        return await self._move_to_next_step(execution)
    
    async def _execute_approval_step(self, execution, step):
        """
        Execute approval step with multi-level routing
        """
        from ..models import DocumentApproval
        
        # Determine approval level
        approval_level = execution.execution_data.get('current_approval_level', 1)
        
        # Create approval record
        approval = DocumentApproval(
            document=execution.document,
            workflow_step=step,
            approval_level=approval_level,
            due_date=timezone.now() + timedelta(hours=24)
        )
        
        # Assign approver
        if step.approver:
            approval.approver = step.approver
        elif step.approval_group:
            # Get approver from group (simplified - in real implementation, use Django groups)
            approver = await self._get_approver_from_group(step.approval_group, approval_level)
            if approver:
                approval.approver = approver
            else:
                return {"status": "failed", "error": "No approver found in group"}
        else:
            return {"status": "failed", "error": "No approver specified"}
        
        await approval.asave()
        
        # Update document status
        execution.document.workflow_status = 'pending'
        execution.document.current_approver = approval.approver
        await execution.document.asave()
        
        # Send approval notification
        await self._send_approval_notification(approval)
        
        # Update execution data
        execution.execution_data['pending_approvals'] = execution.execution_data.get('pending_approvals', [])
        execution.execution_data['pending_approvals'].append(str(approval.id))
        await execution.asave()
        
        return {
            "status": "approval_pending",
            "approval_id": str(approval.id),
            "approver": approval.approver.username,
            "due_date": approval.due_date.isoformat()
        }
    
    async def _get_approver_from_group(self, group_name, level):
        """
        Get approver from approval group based on level
        """
        # This is a simplified implementation
        # In a real system, you'd have proper group management
        try:
            # Get users from group (simplified)
            users = User.objects.filter(groups__name=group_name)
            if level == 1:
                return await users.afirst()
            else:
                # For higher levels, get different approvers
                user_list = [user async for user in users]
                if len(user_list) >= level:
                    return user_list[level - 1]
                return user_list[-1] if user_list else None
        except Exception:
            return None
    
    async def _execute_integration_step(self, execution, step):
        """
        Execute integration step
        """
        from .integration_service import integration_service
        from ..models import IntegrationConfiguration
        
        if not step.integration_system:
            return {"status": "failed", "error": "No integration system specified"}
        
        try:
            # Get integration configuration
            integration_config = await IntegrationConfiguration.objects.aget(
                integration_type=step.integration_system,
                status='active'
            )
            
            # Execute integration
            result = await integration_service.send_to_external_system(
                execution.document,
                integration_config
            )
            
            # Update execution data
            execution.execution_data['integration_results'] = execution.execution_data.get('integration_results', [])
            execution.execution_data['integration_results'].append(result)
            await execution.asave()
            
            if result.get('status') == 'success':
                return await self._move_to_next_step(execution)
            else:
                return {"status": "failed", "error": result.get('error', 'Integration failed')}
                
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _execute_notification_step(self, execution, step):
        """
        Execute notification step
        """
        # Send notification and move to next step
        await self._send_workflow_notification(
            execution.document,
            f"Workflow {execution.workflow.name} - {step.name}",
            step.description,
            execution.workflow
        )
        
        return await self._move_to_next_step(execution)
    
    async def _execute_processing_step(self, execution, step):
        """
        Execute processing step
        """
        # Default processing step - just move to next step
        return await self._move_to_next_step(execution)
    
    async def _move_to_next_step(self, execution):
        """
        Move workflow to next step
        """
        current_step = execution.current_step
        next_step = await execution.workflow.steps.filter(
            step_order=current_step.step_order + 1
        ).afirst()
        
        if next_step:
            execution.current_step = next_step
            execution.execution_data['steps_completed'] = execution.execution_data.get('steps_completed', 0) + 1
            await execution.asave()
            
            # Execute next step
            return await self._execute_workflow_step(execution, next_step)
        else:
            # Workflow completed
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.execution_data['completed_at'] = timezone.now().isoformat()
            await execution.asave()
            
            # Update document status
            execution.document.workflow_status = 'approved'
            execution.document.current_approver = None
            await execution.document.asave()
            
            return {"status": "completed", "message": "Workflow completed successfully"}
    
    async def continue_workflow(self, execution):
        """
        Continue workflow execution after approval or other pause
        """
        try:
            print(f"🔄 Continuing workflow for execution {execution.id}")
            
            # Move to next step
            result = await self._move_to_next_step(execution)
            
            print(f"✅ Workflow continuation result: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Error continuing workflow: {str(e)}")
            execution.status = 'failed'
            execution.error_log = f"Error continuing workflow: {str(e)}"
            await execution.asave()
            return {"status": "failed", "error": str(e)}
    
    async def handle_approval_response(self, approval_id, approver, action, comments=None):
        """
        Handle approval response (approve/reject/delegate)
        """
        from ..models import DocumentApproval
        
        try:
            approval = await DocumentApproval.objects.aget(id=approval_id)
            
            if approval.approver != approver:
                return {"status": "error", "error": "Unauthorized approver"}
            
            # Update approval
            approval.status = action
            approval.comments = comments or ""
            approval.reviewed_at = timezone.now()
            await approval.asave()
            
            # Get workflow execution
            execution = await approval.document.workflow_executions.afirst()
            
            if action == 'approved':
                return await self._handle_approval_approved(approval, execution)
            elif action == 'rejected':
                return await self._handle_approval_rejected(approval, execution)
            elif action == 'delegated':
                return await self._handle_approval_delegated(approval, execution)
            
        except Exception as e:
            logger.error(f"Error handling approval response: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _handle_approval_approved(self, approval, execution):
        """
        Handle approved approval
        """
        # Check if this step requires all approvers
        if approval.workflow_step.requires_all_approvers:
            # Check if all approvers at this level have approved
            pending_approvals = await approval.workflow_step.approvals.filter(
                approval_level=approval.approval_level,
                status='pending'
            ).acount()
            
            if pending_approvals > 0:
                return {"status": "waiting", "message": "Waiting for other approvers"}
        
        # Move to next step
        return await self._move_to_next_step(execution)
    
    async def _handle_approval_rejected(self, approval, execution):
        """
        Handle rejected approval
        """
        # Reject the entire workflow
        execution.status = 'failed'
        execution.error_log = f"Rejected by {approval.approver.username}: {approval.comments}"
        execution.completed_at = timezone.now()
        await execution.asave()
        
        # Update document status
        execution.document.workflow_status = 'rejected'
        execution.document.current_approver = None
        await execution.document.asave()
        
        return {"status": "rejected", "message": f"Workflow rejected by {approval.approver.username}"}
    
    async def _handle_approval_delegated(self, approval, execution):
        """
        Handle delegated approval
        """
        # This would implement delegation logic
        # For now, just return success
        return {"status": "delegated", "message": "Approval delegated successfully"}
    
    async def _send_approval_notification(self, approval):
        """
        Send notification to approver
        """
        subject = f"Document Approval Required: {approval.document.filename}"
        message = f"""
        You have a document pending approval.
        
        Document: {approval.document.filename}
        Type: {approval.document.document_type}
        Workflow: {approval.workflow_step.workflow.name}
        Step: {approval.workflow_step.name}
        Due Date: {approval.due_date}
        
        Please review and approve/reject this document.
        """
        
        await self._send_email_notification(
            approval.approver.email,
            subject,
            message
        )
    
    async def _send_workflow_notification(self, document, subject, message, workflow):
        """
        Send workflow notification
        """
        from ..models import Notification
        
        # Create notification record
        notification = Notification(
            recipient_email="admin@example.com",  # This should be configurable
            subject=subject,
            message=message,
            document=document,
            workflow=workflow
        )
        await notification.asave()
        
        # Send email
        await self._send_email_notification(
            notification.recipient_email,
            subject,
            message
        )
    
    async def _send_email_notification(self, recipient_email, subject, message):
        """
        Send email notification
        """
        try:
            # Use Django's email functionality
            await sync_to_async(send_mail)(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
            return False

# Global service instance
workflow_service = AdvancedWorkflowService()

# Legacy compatibility functions
async def start_document_workflow(document, workflow):
    """
    Start a document workflow
    """
    return await workflow_service.start_document_workflow(document, workflow)

async def send_email_notification(notification):
    """
    Send an email notification
    """
    try:
        await workflow_service._send_email_notification(
            notification.recipient_email,
            notification.subject,
            notification.message
        )
        
        notification.sent_status = "sent"
        notification.sent_at = timezone.now()
        await notification.asave()
        
        return True
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        
        notification.sent_status = "failed"
        await notification.asave()
        
        return False

async def process_document_in_workflow(document_id, workflow_id, started_by=None):
    """
    Process a document through a workflow
    """
    from ..models import Document, Workflow
    
    try:
        document = await Document.objects.aget(id=document_id)
        workflow = await Workflow.objects.aget(id=workflow_id)
        
        return await workflow_service.start_document_workflow(document, workflow, started_by)
    except Document.DoesNotExist:
        return {
            "status": "failed",
            "error": f"Document with ID {document_id} not found"
        }
    except Workflow.DoesNotExist:
        return {
            "status": "failed",
            "error": f"Workflow with ID {workflow_id} not found"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }

async def get_workflow_templates():
    """
    Get all available workflow templates
    """
    from ..models import Workflow
    
    workflows = []
    async for workflow in Workflow.objects.filter(is_active=True):
        steps = []
        async for step in workflow.steps.all():
            steps.append({
                "id": str(step.id),
                "name": step.name,
                "description": step.description,
                "step_order": step.step_order,
                "step_type": step.step_type,
                "approver": step.approver.username if step.approver else None,
                "approval_group": step.approval_group,
                "requires_all_approvers": step.requires_all_approvers
            })
            
        workflows.append({
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "steps": steps,
            "requires_approval": workflow.requires_approval,
            "approval_threshold": float(workflow.approval_threshold) if workflow.approval_threshold else None
        })
        
    return workflows

async def create_workflow(name, description, steps, requires_approval=False, approval_threshold=None):
    """
    Create a new workflow with the specified steps
    """
    from ..models import Workflow, WorkflowStep
    
    # Create the workflow
    workflow = Workflow(
        name=name,
        description=description,
        requires_approval=requires_approval,
        approval_threshold=approval_threshold
    )
    await workflow.asave()
    
    # Create the steps
    for step in steps:
        workflow_step = WorkflowStep(
            workflow=workflow,
            name=step["name"],
            description=step["description"],
            step_order=step["step_order"],
            step_type=step.get("step_type", "processing"),
            approval_group=step.get("approval_group"),
            requires_all_approvers=step.get("requires_all_approvers", False),
            integration_system=step.get("integration_system"),
            integration_config=step.get("integration_config"),
            condition_field=step.get("condition_field"),
            condition_value=step.get("condition_value"),
            condition_operator=step.get("condition_operator")
        )
        await workflow_step.asave()
        
    return workflow

async def send_workflow_notification(recipient_email, subject, message, document_id=None, workflow_id=None):
    """
    Send a notification about a workflow
    """
    from ..models import Notification, Document, Workflow
    
    try:
        document = None
        workflow = None
        
        if document_id:
            document = await Document.objects.aget(id=document_id)
            
        if workflow_id:
            workflow = await Workflow.objects.aget(id=workflow_id)
            
        notification = Notification(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            document=document,
            workflow=workflow
        )
        await notification.asave()
        
        return await send_email_notification(notification)
    except Exception as e:
        logger.error(f"Error sending workflow notification: {str(e)}")
        return False 