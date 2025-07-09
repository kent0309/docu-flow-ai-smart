import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.utils import timezone

async def start_document_workflow(document, workflow):
    """
    Start a document workflow by finding the first step and creating a notification
    
    Args:
        document: The document to process
        workflow: The workflow to use
        
    Returns:
        dict: Details about the started workflow
    """
    try:
        # Get the first step in the workflow
        first_step = await workflow.steps.filter(step_order=1).afirst()
        
        if not first_step:
            return {
                "status": "failed",
                "error": "No steps defined in this workflow",
                "workflow_id": str(workflow.id),
                "workflow_name": workflow.name
            }
        
        # Create a notification for this step
        from ..models import Notification
        notification = Notification(
            recipient_email="user@example.com",  # This would be configured per workflow
            subject=f"Document requires approval: {document.filename}",
            message=f"Please review the document '{document.filename}' as part of the workflow '{workflow.name}'.",
            document=document,
            workflow=workflow,
        )
        await notification.asave()
        
        # Send the notification email
        await send_email_notification(notification)
        
        # Return information about the started workflow
        return {
            "status": "started",
            "document_id": str(document.id),
            "workflow_id": str(workflow.id),
            "workflow_name": workflow.name,
            "step_name": first_step.name,
            "notification_id": str(notification.id)
        }
        
    except Exception as e:
        print(f"Error starting workflow: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "workflow_id": str(workflow.id),
            "workflow_name": workflow.name
        }

async def send_email_notification(notification):
    """
    Send an email notification (placeholder implementation)
    
    Args:
        notification: The notification object to send
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # In a real implementation, this would connect to an email service
        print(f"Sending approval email to {notification.recipient_email}: {notification.subject}")
        
        # Simulate sending the email
        notification.sent_status = "sent"
        notification.sent_at = timezone.now()
        await notification.asave()
        
        return True
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        
        # Update notification status to failed
        notification.sent_status = "failed"
        await notification.asave()
        
        return False

async def process_document_in_workflow(document_id, workflow_id):
    """
    Process a document through a workflow
    
    Args:
        document_id: The ID of the document to process
        workflow_id: The ID of the workflow to use
        
    Returns:
        dict: The result of the workflow processing
    """
    from ..models import Document, Workflow
    
    try:
        # Get the document and workflow
        document = await Document.objects.aget(id=document_id)
        workflow = await Workflow.objects.aget(id=workflow_id)
        
        # Start the workflow
        result = await start_document_workflow(document, workflow)
        
        return result
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
    
    Returns:
        List[Dict]: A list of workflow templates
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
                "step_order": step.step_order
            })
            
        workflows.append({
            "id": str(workflow.id),
            "name": workflow.name,
            "description": workflow.description,
            "steps": steps
        })
        
    return workflows

async def create_workflow(name, description, steps):
    """
    Create a new workflow with the specified steps
    
    Args:
        name (str): The name of the workflow
        description (str): The description of the workflow
        steps (List[Dict]): A list of steps with name, description, and order
        
    Returns:
        Workflow: The created workflow
    """
    from ..models import Workflow, WorkflowStep
    
    # Create the workflow
    workflow = Workflow(name=name, description=description)
    await workflow.asave()
    
    # Create the steps
    for step in steps:
        workflow_step = WorkflowStep(
            workflow=workflow,
            name=step["name"],
            description=step["description"],
            step_order=step["step_order"]
        )
        await workflow_step.asave()
        
    return workflow

async def send_workflow_notification(recipient_email, subject, message, document_id=None, workflow_id=None):
    """
    Send a notification about a workflow
    
    Args:
        recipient_email (str): The email address to send to
        subject (str): The subject of the notification
        message (str): The message content
        document_id (str, optional): The ID of the document
        workflow_id (str, optional): The ID of the workflow
        
    Returns:
        bool: True if sent successfully, False otherwise
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
        print(f"Error sending workflow notification: {str(e)}")
        return False 