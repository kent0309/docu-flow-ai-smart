from django.core.management.base import BaseCommand
from django.db import transaction
from documents_api.models import IntegrationConfiguration
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Sets up predefined integration templates for different business types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--business-type',
            type=str,
            choices=['restaurant', 'retail', 'manufacturing', 'healthcare', 'construction', 'all'],
            default='all',
            help='Business type to set up integration templates for'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing integration templates'
        )

    def handle(self, *args, **options):
        business_type = options['business_type']
        overwrite = options['overwrite']
        
        self.stdout.write(self.style.SUCCESS(f'Setting up integration templates for: {business_type}'))
        
        with transaction.atomic():
            if business_type == 'all':
                self.setup_restaurant_integrations(overwrite)
                self.setup_retail_integrations(overwrite)
                self.setup_manufacturing_integrations(overwrite)
                self.setup_healthcare_integrations(overwrite)
                self.setup_construction_integrations(overwrite)
            elif business_type == 'restaurant':
                self.setup_restaurant_integrations(overwrite)
            elif business_type == 'retail':
                self.setup_retail_integrations(overwrite)
            elif business_type == 'manufacturing':
                self.setup_manufacturing_integrations(overwrite)
            elif business_type == 'healthcare':
                self.setup_healthcare_integrations(overwrite)
            elif business_type == 'construction':
                self.setup_construction_integrations(overwrite)
        
        self.stdout.write(self.style.SUCCESS('Integration templates setup completed!'))

    def setup_restaurant_integrations(self, overwrite=False):
        """Set up integration templates for restaurant business"""
        self.stdout.write('Setting up restaurant integration templates...')
        
        restaurant_integrations = [
            {
                'name': 'Restaurant QuickBooks Integration',
                'integration_type': 'quickbooks',
                'description': 'Connect to QuickBooks for restaurant accounting and invoice processing',
                'supported_document_types': ['restaurant_invoice', 'restaurant_receipt', 'restaurant_purchase_order'],
                'config_data': {
                    'sync_frequency': 30,
                    'auto_categorize': True,
                    'chart_of_accounts': {
                        'food_costs': '5000',
                        'beverage_costs': '5100',
                        'supplies': '5200',
                        'equipment': '1500'
                    },
                    'tax_settings': {
                        'sales_tax_rate': 0.0875,
                        'food_tax_exempt': True,
                        'beverage_tax_exempt': False
                    },
                    'validation_rules': {
                        'require_receipt_number': True,
                        'validate_food_safety_cert': True,
                        'check_supplier_license': True
                    }
                },
                'status': 'inactive'
            },
            {
                'name': 'Restaurant POS Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with restaurant POS system for sales data',
                'supported_document_types': ['restaurant_receipt', 'daily_sales_report'],
                'config_data': {
                    'api_version': 'v2',
                    'sync_frequency': 15,
                    'real_time_sync': True,
                    'data_mapping': {
                        'table_number': 'table_id',
                        'server_id': 'employee_id',
                        'order_items': 'line_items',
                        'payment_method': 'tender_type'
                    },
                    'pos_specific': {
                        'track_inventory': True,
                        'sync_menu_items': True,
                        'calculate_labor_costs': True
                    }
                },
                'status': 'inactive'
            },
            {
                'name': 'Restaurant Inventory Management',
                'integration_type': 'custom_api',
                'description': 'Integration with inventory management system for stock tracking',
                'supported_document_types': ['restaurant_invoice', 'restaurant_purchase_order', 'inventory_receipt'],
                'config_data': {
                    'auto_update_inventory': True,
                    'track_expiration_dates': True,
                    'perishable_item_alerts': True,
                    'reorder_point_calculation': True,
                    'waste_tracking': True,
                    'cost_calculation': {
                        'method': 'FIFO',
                        'include_labor': False,
                        'include_overhead': True
                    }
                },
                'status': 'inactive'
            },
            {
                'name': 'Restaurant Food Safety Compliance',
                'integration_type': 'webhook',
                'description': 'Integration with food safety compliance system',
                'supported_document_types': ['restaurant_invoice', 'food_safety_cert', 'supplier_audit'],
                'config_data': {
                    'compliance_checks': {
                        'temperature_logs': True,
                        'supplier_certifications': True,
                        'expiration_tracking': True,
                        'allergen_information': True
                    },
                    'notification_settings': {
                        'cert_expiration_days': 30,
                        'supplier_audit_frequency': 90,
                        'temperature_violation_immediate': True
                    }
                },
                'status': 'inactive'
            }
        ]
        
        self._create_integration_templates(restaurant_integrations, overwrite)

    def setup_retail_integrations(self, overwrite=False):
        """Set up integration templates for retail business"""
        self.stdout.write('Setting up retail integration templates...')
        
        retail_integrations = [
            {
                'name': 'Retail Shopify Integration',
                'integration_type': 'custom_api',
                'description': 'Connect to Shopify for e-commerce order processing',
                'supported_document_types': ['retail_invoice', 'retail_receipt', 'shipping_label'],
                'config_data': {
                    'auto_sync_orders': True,
                    'inventory_sync': True,
                    'product_sync': True,
                    'customer_sync': True,
                    'order_processing': {
                        'auto_fulfill': True,
                        'print_labels': True,
                        'update_tracking': True
                    }
                },
                'status': 'inactive'
            },
            {
                'name': 'Retail Square POS Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with Square POS for in-store sales',
                'supported_document_types': ['retail_receipt', 'daily_sales_report'],
                'config_data': {
                    'payment_processing': True,
                    'inventory_tracking': True,
                    'customer_management': True,
                    'employee_management': True,
                    'reporting': {
                        'daily_sales': True,
                        'inventory_levels': True,
                        'employee_performance': True
                    }
                },
                'status': 'inactive'
            },
            {
                'name': 'Retail WooCommerce Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with WooCommerce for WordPress-based stores',
                'supported_document_types': ['retail_invoice', 'retail_receipt'],
                'config_data': {
                    'order_sync': True,
                    'product_sync': True,
                    'customer_sync': True,
                    'inventory_management': True,
                    'tax_calculation': True
                },
                'status': 'inactive'
            }
        ]
        
        self._create_integration_templates(retail_integrations, overwrite)

    def setup_manufacturing_integrations(self, overwrite=False):
        """Set up integration templates for manufacturing business"""
        self.stdout.write('Setting up manufacturing integration templates...')
        
        manufacturing_integrations = [
            {
                'name': 'Manufacturing SAP ERP Integration',
                'integration_type': 'sap_erp',
                'description': 'Integration with SAP ERP for manufacturing operations',
                'supported_document_types': ['manufacturing_invoice', 'manufacturing_purchase_order', 'quality_certificate'],
                'config_data': {
                    'modules': ['MM', 'PP', 'QM', 'FI'],
                    'material_management': True,
                    'production_planning': True,
                    'quality_management': True,
                    'financial_integration': True,
                    'batch_tracking': True,
                    'compliance_reporting': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Manufacturing MES Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with Manufacturing Execution System',
                'supported_document_types': ['production_order', 'quality_report', 'material_consumption'],
                'config_data': {
                    'real_time_tracking': True,
                    'quality_control': True,
                    'equipment_monitoring': True,
                    'labor_tracking': True,
                    'material_tracking': True,
                    'performance_metrics': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Manufacturing Quality Management',
                'integration_type': 'custom_api',
                'description': 'Integration with Quality Management System',
                'supported_document_types': ['quality_certificate', 'inspection_report', 'calibration_record'],
                'config_data': {
                    'inspection_scheduling': True,
                    'certificate_management': True,
                    'non_conformance_tracking': True,
                    'corrective_actions': True,
                    'statistical_process_control': True
                },
                'status': 'inactive'
            }
        ]
        
        self._create_integration_templates(manufacturing_integrations, overwrite)

    def setup_healthcare_integrations(self, overwrite=False):
        """Set up integration templates for healthcare business"""
        self.stdout.write('Setting up healthcare integration templates...')
        
        healthcare_integrations = [
            {
                'name': 'Healthcare EMR Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with Electronic Medical Records system',
                'supported_document_types': ['healthcare_invoice', 'medical_record', 'prescription'],
                'config_data': {
                    'patient_management': True,
                    'appointment_scheduling': True,
                    'billing_integration': True,
                    'prescription_management': True,
                    'lab_results_integration': True,
                    'hipaa_compliance': True,
                    'audit_logging': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Healthcare Insurance Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with insurance claim processing systems',
                'supported_document_types': ['healthcare_invoice', 'insurance_claim', 'eob'],
                'config_data': {
                    'claim_submission': True,
                    'eligibility_verification': True,
                    'prior_authorization': True,
                    'payment_posting': True,
                    'denial_management': True,
                    'reporting': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Healthcare Lab Integration',
                'integration_type': 'custom_api',
                'description': 'Integration with laboratory information systems',
                'supported_document_types': ['lab_order', 'lab_result', 'pathology_report'],
                'config_data': {
                    'order_management': True,
                    'result_reporting': True,
                    'critical_value_alerts': True,
                    'quality_control': True,
                    'regulatory_compliance': True
                },
                'status': 'inactive'
            }
        ]
        
        self._create_integration_templates(healthcare_integrations, overwrite)

    def setup_construction_integrations(self, overwrite=False):
        """Set up integration templates for construction business"""
        self.stdout.write('Setting up construction integration templates...')
        
        construction_integrations = [
            {
                'name': 'Construction Project Management',
                'integration_type': 'custom_api',
                'description': 'Integration with construction project management software',
                'supported_document_types': ['construction_invoice', 'construction_purchase_order', 'project_report'],
                'config_data': {
                    'project_tracking': True,
                    'resource_management': True,
                    'scheduling': True,
                    'budget_management': True,
                    'progress_reporting': True,
                    'document_management': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Construction Safety Management',
                'integration_type': 'custom_api',
                'description': 'Integration with safety management systems',
                'supported_document_types': ['safety_report', 'incident_report', 'inspection_checklist'],
                'config_data': {
                    'incident_tracking': True,
                    'safety_training': True,
                    'compliance_monitoring': True,
                    'inspection_scheduling': True,
                    'reporting': True
                },
                'status': 'inactive'
            },
            {
                'name': 'Construction Equipment Management',
                'integration_type': 'custom_api',
                'description': 'Integration with equipment management systems',
                'supported_document_types': ['equipment_invoice', 'maintenance_record', 'rental_agreement'],
                'config_data': {
                    'asset_tracking': True,
                    'maintenance_scheduling': True,
                    'utilization_tracking': True,
                    'cost_management': True,
                    'depreciation_tracking': True
                },
                'status': 'inactive'
            }
        ]
        
        self._create_integration_templates(construction_integrations, overwrite)

    def _create_integration_templates(self, integrations, overwrite=False):
        """Create integration templates from definitions"""
        for integration_def in integrations:
            integration_name = integration_def['name']
            
            # Check if integration already exists
            existing_integration = IntegrationConfiguration.objects.filter(name=integration_name).first()
            
            if existing_integration:
                if overwrite:
                    self.stdout.write(f'  Updating existing integration: {integration_name}')
                    for key, value in integration_def.items():
                        setattr(existing_integration, key, value)
                    existing_integration.save()
                else:
                    self.stdout.write(f'  Skipping existing integration: {integration_name}')
                    continue
            else:
                self.stdout.write(f'  Creating new integration template: {integration_name}')
                IntegrationConfiguration.objects.create(**integration_def) 