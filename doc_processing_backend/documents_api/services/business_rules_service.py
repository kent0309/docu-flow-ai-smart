from typing import Dict, List, Optional, Any
from asgiref.sync import sync_to_async
from django.db.models import Q
from ..models import ValidationRule, Workflow, WorkflowStep, IntegrationConfiguration

class BusinessRulesService:
    """
    Service for managing business-specific rules and applying them based on business type
    """
    
    # Business type mappings
    BUSINESS_TYPES = {
        'restaurant': {
            'name': 'Restaurant',
            'description': 'Food service and hospitality business',
            'document_types': ['restaurant_invoice', 'restaurant_receipt', 'restaurant_purchase_order', 
                             'food_safety_cert', 'supplier_audit', 'inventory_receipt'],
            'key_features': ['food_safety_compliance', 'perishable_item_tracking', 'pos_integration', 
                           'inventory_management', 'supplier_management']
        },
        'retail': {
            'name': 'Retail',
            'description': 'Retail sales and e-commerce business',
            'document_types': ['retail_invoice', 'retail_receipt', 'shipping_label', 'daily_sales_report'],
            'key_features': ['inventory_sync', 'pos_integration', 'ecommerce_integration', 
                           'customer_management', 'product_catalog']
        },
        'manufacturing': {
            'name': 'Manufacturing',
            'description': 'Manufacturing and production business',
            'document_types': ['manufacturing_invoice', 'manufacturing_purchase_order', 'quality_certificate',
                             'production_order', 'quality_report', 'material_consumption'],
            'key_features': ['quality_control', 'batch_tracking', 'erp_integration', 
                           'production_planning', 'compliance_reporting']
        },
        'healthcare': {
            'name': 'Healthcare',
            'description': 'Healthcare and medical services',
            'document_types': ['healthcare_invoice', 'medical_record', 'prescription', 'insurance_claim',
                             'eob', 'lab_order', 'lab_result', 'pathology_report'],
            'key_features': ['hipaa_compliance', 'emr_integration', 'insurance_processing', 
                           'patient_management', 'regulatory_compliance']
        },
        'construction': {
            'name': 'Construction',
            'description': 'Construction and building services',
            'document_types': ['construction_invoice', 'construction_purchase_order', 'project_report',
                             'safety_report', 'incident_report', 'inspection_checklist'],
            'key_features': ['project_management', 'safety_compliance', 'permit_tracking', 
                           'equipment_management', 'regulatory_compliance']
        }
    }
    
    def __init__(self):
        self.active_business_types = []
    
    async def get_available_business_types(self) -> Dict[str, Any]:
        """
        Get all available business types with their configurations
        """
        business_types_with_rules = {}
        
        for business_type, config in self.BUSINESS_TYPES.items():
            # Count rules for this business type
            rule_count = await self._get_rule_count_for_business_type(business_type)
            integration_count = await self._get_integration_count_for_business_type(business_type)
            
            business_types_with_rules[business_type] = {
                **config,
                'validation_rules_count': rule_count,
                'integration_templates_count': integration_count,
                'is_configured': rule_count > 0
            }
        
        return business_types_with_rules
    
    async def get_business_type_rules(self, business_type: str) -> Dict[str, Any]:
        """
        Get all rules and configurations for a specific business type
        """
        if business_type not in self.BUSINESS_TYPES:
            raise ValueError(f"Unknown business type: {business_type}")
        
        @sync_to_async
        def get_rules():
            return list(ValidationRule.objects.filter(
                document_type__in=self.BUSINESS_TYPES[business_type]['document_types'],
                is_active=True
            ).values())
        
        @sync_to_async
        def get_workflows():
            return list(Workflow.objects.filter(
                name__icontains=business_type.replace('_', ' '),
                is_active=True
            ).values())
        
        @sync_to_async
        def get_integrations():
            return list(IntegrationConfiguration.objects.filter(
                name__icontains=business_type.replace('_', ' ')
            ).values())
        
        rules = await get_rules()
        workflows = await get_workflows()
        integrations = await get_integrations()
        
        return {
            'business_type': business_type,
            'config': self.BUSINESS_TYPES[business_type],
            'validation_rules': rules,
            'workflows': workflows,
            'integration_templates': integrations
        }
    
    async def activate_business_type_rules(self, business_type: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Activate rules for a specific business type
        """
        if business_type not in self.BUSINESS_TYPES:
            raise ValueError(f"Unknown business type: {business_type}")
        
        @sync_to_async
        def activate_rules():
            # Activate validation rules
            rules_updated = ValidationRule.objects.filter(
                document_type__in=self.BUSINESS_TYPES[business_type]['document_types']
            ).update(is_active=True)
            
            # Activate workflows
            workflows_updated = Workflow.objects.filter(
                name__icontains=business_type.replace('_', ' ')
            ).update(is_active=True)
            
            return rules_updated, workflows_updated
        
        rules_count, workflows_count = await activate_rules()
        
        return {
            'business_type': business_type,
            'activated_rules': rules_count,
            'activated_workflows': workflows_count,
            'status': 'activated'
        }
    
    async def deactivate_business_type_rules(self, business_type: str) -> Dict[str, Any]:
        """
        Deactivate rules for a specific business type
        """
        if business_type not in self.BUSINESS_TYPES:
            raise ValueError(f"Unknown business type: {business_type}")
        
        @sync_to_async
        def deactivate_rules():
            # Deactivate validation rules
            rules_updated = ValidationRule.objects.filter(
                document_type__in=self.BUSINESS_TYPES[business_type]['document_types']
            ).update(is_active=False)
            
            # Deactivate workflows
            workflows_updated = Workflow.objects.filter(
                name__icontains=business_type.replace('_', ' ')
            ).update(is_active=False)
            
            return rules_updated, workflows_updated
        
        rules_count, workflows_count = await deactivate_rules()
        
        return {
            'business_type': business_type,
            'deactivated_rules': rules_count,
            'deactivated_workflows': workflows_count,
            'status': 'deactivated'
        }
    
    async def get_document_type_rules(self, document_type: str) -> List[Dict[str, Any]]:
        """
        Get validation rules for a specific document type
        """
        @sync_to_async
        def get_rules():
            return list(ValidationRule.objects.filter(
                document_type=document_type,
                is_active=True
            ).values())
        
        return await get_rules()
    
    async def validate_document_against_business_rules(self, document_data: Dict[str, Any], 
                                                     document_type: str) -> Dict[str, Any]:
        """
        Validate a document against business-specific rules
        """
        from .validation_service import ValidationEngine
        
        # Get business type from document type
        business_type = self._get_business_type_from_document_type(document_type)
        
        if not business_type:
            return {
                'status': 'no_business_type',
                'message': f'No business type found for document type: {document_type}'
            }
        
        # Use the validation engine
        validation_engine = ValidationEngine()
        validation_result = await validation_engine.validate_document_data(document_data, document_type)
        
        # Add business type specific information
        validation_result['business_type'] = business_type
        validation_result['business_config'] = self.BUSINESS_TYPES[business_type]
        
        return validation_result
    
    async def get_recommended_integrations(self, business_type: str) -> List[Dict[str, Any]]:
        """
        Get recommended integrations for a business type
        """
        if business_type not in self.BUSINESS_TYPES:
            raise ValueError(f"Unknown business type: {business_type}")
        
        @sync_to_async
        def get_integrations():
            return list(IntegrationConfiguration.objects.filter(
                name__icontains=business_type.replace('_', ' ')
            ).values())
        
        integrations = await get_integrations()
        
        # Add recommendation scores based on business type features
        for integration in integrations:
            integration['recommendation_score'] = self._calculate_integration_score(
                integration, business_type
            )
        
        # Sort by recommendation score
        integrations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return integrations
    
    def _get_business_type_from_document_type(self, document_type: str) -> Optional[str]:
        """
        Get business type from document type
        """
        for business_type, config in self.BUSINESS_TYPES.items():
            if document_type in config['document_types']:
                return business_type
        return None
    
    def _calculate_integration_score(self, integration: Dict[str, Any], business_type: str) -> float:
        """
        Calculate recommendation score for an integration
        """
        score = 0.0
        
        # Base score for business type match
        if business_type.replace('_', ' ') in integration['name'].lower():
            score += 10.0
        
        # Score based on supported document types
        business_config = self.BUSINESS_TYPES[business_type]
        supported_types = integration.get('supported_document_types', [])
        
        if supported_types:
            match_count = len(set(supported_types) & set(business_config['document_types']))
            score += (match_count / len(business_config['document_types'])) * 5.0
        
        # Score based on integration type
        integration_type = integration.get('integration_type', '')
        if integration_type in ['quickbooks', 'sap_erp', 'salesforce']:
            score += 3.0
        elif integration_type == 'custom_api':
            score += 2.0
        elif integration_type == 'webhook':
            score += 1.0
        
        return score
    
    async def _get_rule_count_for_business_type(self, business_type: str) -> int:
        """
        Get the count of validation rules for a business type
        """
        if business_type not in self.BUSINESS_TYPES:
            return 0
        
        @sync_to_async
        def count_rules():
            return ValidationRule.objects.filter(
                document_type__in=self.BUSINESS_TYPES[business_type]['document_types']
            ).count()
        
        return await count_rules()
    
    async def _get_integration_count_for_business_type(self, business_type: str) -> int:
        """
        Get the count of integration templates for a business type
        """
        @sync_to_async
        def count_integrations():
            return IntegrationConfiguration.objects.filter(
                name__icontains=business_type.replace('_', ' ')
            ).count()
        
        return await count_integrations()


# Convenience functions for easy access
async def get_available_business_types():
    """Get all available business types"""
    service = BusinessRulesService()
    return await service.get_available_business_types()

async def activate_business_rules(business_type: str, user_id: Optional[int] = None):
    """Activate rules for a business type"""
    service = BusinessRulesService()
    return await service.activate_business_type_rules(business_type, user_id)

async def get_business_type_configuration(business_type: str):
    """Get configuration for a business type"""
    service = BusinessRulesService()
    return await service.get_business_type_rules(business_type)

async def validate_document_with_business_rules(document_data: Dict[str, Any], document_type: str):
    """Validate document against business rules"""
    service = BusinessRulesService()
    return await service.validate_document_against_business_rules(document_data, document_type)

async def get_recommended_integrations_for_business(business_type: str):
    """Get recommended integrations for a business type"""
    service = BusinessRulesService()
    return await service.get_recommended_integrations(business_type) 