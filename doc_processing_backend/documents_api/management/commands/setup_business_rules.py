from django.core.management.base import BaseCommand
from django.db import transaction
from documents_api.models import ValidationRule, Workflow, WorkflowStep, IntegrationConfiguration
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Sets up predefined business workflow rules for different industries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--business-type',
            type=str,
            choices=['restaurant', 'retail', 'manufacturing', 'healthcare', 'construction', 'all'],
            default='all',
            help='Business type to set up rules for'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing rules'
        )

    def handle(self, *args, **options):
        business_type = options['business_type']
        overwrite = options['overwrite']
        
        self.stdout.write(self.style.SUCCESS(f'Setting up business rules for: {business_type}'))
        
        with transaction.atomic():
            if business_type == 'all':
                self.setup_restaurant_rules(overwrite)
                self.setup_retail_rules(overwrite)
                self.setup_manufacturing_rules(overwrite)
                self.setup_healthcare_rules(overwrite)
                self.setup_construction_rules(overwrite)
            elif business_type == 'restaurant':
                self.setup_restaurant_rules(overwrite)
            elif business_type == 'retail':
                self.setup_retail_rules(overwrite)
            elif business_type == 'manufacturing':
                self.setup_manufacturing_rules(overwrite)
            elif business_type == 'healthcare':
                self.setup_healthcare_rules(overwrite)
            elif business_type == 'construction':
                self.setup_construction_rules(overwrite)
        
        self.stdout.write(self.style.SUCCESS('Business rules setup completed!'))

    def setup_restaurant_rules(self, overwrite=False):
        """Set up validation rules for restaurant business"""
        self.stdout.write('Setting up restaurant business rules...')
        
        # Restaurant Invoice Rules
        restaurant_invoice_rules = [
            {
                'name': 'Restaurant Invoice - Supplier Required',
                'document_type': 'restaurant_invoice',
                'field_name': 'supplier_name',
                'rule_type': 'required',
                'rule_pattern': '',
                'description': 'Supplier name is mandatory for restaurant invoices'
            },
            {
                'name': 'Restaurant Invoice - Food Safety Certificate',
                'document_type': 'restaurant_invoice',
                'field_name': 'food_safety_cert',
                'rule_type': 'regex',
                'rule_pattern': r'^[A-Z]{2,3}-\d{4}-\d{4}$',
                'description': 'Food safety certification number format validation'
            },
            {
                'name': 'Restaurant Invoice - Perishable Item Flag',
                'document_type': 'restaurant_invoice',
                'field_name': 'perishable_items',
                'rule_type': 'enum',
                'rule_pattern': 'yes,no,partial',
                'description': 'Indicates if invoice contains perishable items'
            },
            {
                'name': 'Restaurant Invoice - Total Amount Range',
                'document_type': 'restaurant_invoice',
                'field_name': 'total_amount',
                'rule_type': 'range',
                'rule_pattern': '0,50000',
                'description': 'Total amount should be within reasonable range'
            },
            {
                'name': 'Restaurant Invoice - Line Items Total',
                'document_type': 'restaurant_invoice',
                'field_name': 'total_amount',
                'rule_type': 'cross_reference',
                'rule_pattern': 'line_items',
                'description': 'Total amount should match sum of line items',
                'reference_field': 'line_items',
                'calculation_type': 'sum',
                'tolerance': 0.01
            }
        ]
        
        # Restaurant Receipt Rules
        restaurant_receipt_rules = [
            {
                'name': 'Restaurant Receipt - Table Number',
                'document_type': 'restaurant_receipt',
                'field_name': 'table_number',
                'rule_type': 'range',
                'rule_pattern': '1,100',
                'description': 'Table number should be within valid range'
            },
            {
                'name': 'Restaurant Receipt - Payment Method',
                'document_type': 'restaurant_receipt',
                'field_name': 'payment_method',
                'rule_type': 'enum',
                'rule_pattern': 'cash,card,mobile,check',
                'description': 'Payment method validation'
            },
            {
                'name': 'Restaurant Receipt - Tip Amount',
                'document_type': 'restaurant_receipt',
                'field_name': 'tip_amount',
                'rule_type': 'range',
                'rule_pattern': '0,1000',
                'description': 'Tip amount should be reasonable'
            },
            {
                'name': 'Restaurant Receipt - Order Items Required',
                'document_type': 'restaurant_receipt',
                'field_name': 'order_items',
                'rule_type': 'required',
                'rule_pattern': '',
                'description': 'Order items must be present'
            }
        ]
        
        # Restaurant Purchase Order Rules
        restaurant_po_rules = [
            {
                'name': 'Restaurant PO - Delivery Date',
                'document_type': 'restaurant_purchase_order',
                'field_name': 'delivery_date',
                'rule_type': 'date',
                'rule_pattern': '',
                'description': 'Delivery date must be valid'
            },
            {
                'name': 'Restaurant PO - Priority Level',
                'document_type': 'restaurant_purchase_order',
                'field_name': 'priority',
                'rule_type': 'enum',
                'rule_pattern': 'low,medium,high,urgent',
                'description': 'Priority level validation'
            },
            {
                'name': 'Restaurant PO - Approval Required',
                'document_type': 'restaurant_purchase_order',
                'field_name': 'total_amount',
                'rule_type': 'range',
                'rule_pattern': '0,5000',
                'description': 'Purchase orders above $5000 need special approval'
            }
        ]
        
        self._create_validation_rules(restaurant_invoice_rules + restaurant_receipt_rules + restaurant_po_rules, overwrite)
        
        # Create Restaurant Workflow
        self._create_restaurant_workflow(overwrite)

    def setup_retail_rules(self, overwrite=False):
        """Set up validation rules for retail business"""
        self.stdout.write('Setting up retail business rules...')
        
        retail_rules = [
            {
                'name': 'Retail Invoice - SKU Format',
                'document_type': 'retail_invoice',
                'field_name': 'sku',
                'rule_type': 'regex',
                'rule_pattern': r'^[A-Z]{2,3}-\d{6,12}$',
                'description': 'SKU format validation for retail products'
            },
            {
                'name': 'Retail Invoice - Product Category',
                'document_type': 'retail_invoice',
                'field_name': 'product_category',
                'rule_type': 'enum',
                'rule_pattern': 'electronics,clothing,home,books,toys,sports,beauty,automotive',
                'description': 'Valid product categories'
            },
            {
                'name': 'Retail Invoice - Discount Percentage',
                'document_type': 'retail_invoice',
                'field_name': 'discount_percentage',
                'rule_type': 'range',
                'rule_pattern': '0,75',
                'description': 'Discount percentage should be reasonable'
            },
            {
                'name': 'Retail Receipt - Store Location',
                'document_type': 'retail_receipt',
                'field_name': 'store_location',
                'rule_type': 'required',
                'rule_pattern': '',
                'description': 'Store location is mandatory'
            },
            {
                'name': 'Retail Receipt - Cashier ID',
                'document_type': 'retail_receipt',
                'field_name': 'cashier_id',
                'rule_type': 'regex',
                'rule_pattern': r'^EMP-\d{4,6}$',
                'description': 'Cashier ID format validation'
            }
        ]
        
        self._create_validation_rules(retail_rules, overwrite)

    def setup_manufacturing_rules(self, overwrite=False):
        """Set up validation rules for manufacturing business"""
        self.stdout.write('Setting up manufacturing business rules...')
        
        manufacturing_rules = [
            {
                'name': 'Manufacturing Invoice - Part Number',
                'document_type': 'manufacturing_invoice',
                'field_name': 'part_number',
                'rule_type': 'regex',
                'rule_pattern': r'^[A-Z]{2,4}-\d{4,8}-[A-Z]{1,2}$',
                'description': 'Manufacturing part number format'
            },
            {
                'name': 'Manufacturing Invoice - Quality Certificate',
                'document_type': 'manufacturing_invoice',
                'field_name': 'quality_cert',
                'rule_type': 'required',
                'rule_pattern': '',
                'description': 'Quality certificate is required'
            },
            {
                'name': 'Manufacturing Invoice - Batch Number',
                'document_type': 'manufacturing_invoice',
                'field_name': 'batch_number',
                'rule_type': 'regex',
                'rule_pattern': r'^BATCH-\d{6}-\d{4}$',
                'description': 'Batch number format validation'
            },
            {
                'name': 'Manufacturing PO - Material Specifications',
                'document_type': 'manufacturing_purchase_order',
                'field_name': 'material_specs',
                'rule_type': 'required',
                'rule_pattern': '',
                'description': 'Material specifications must be provided'
            },
            {
                'name': 'Manufacturing PO - Quantity Range',
                'document_type': 'manufacturing_purchase_order',
                'field_name': 'quantity',
                'rule_type': 'range',
                'rule_pattern': '1,100000',
                'description': 'Quantity should be within reasonable range'
            }
        ]
        
        self._create_validation_rules(manufacturing_rules, overwrite)

    def setup_healthcare_rules(self, overwrite=False):
        """Set up validation rules for healthcare business"""
        self.stdout.write('Setting up healthcare business rules...')
        
        healthcare_rules = [
            {
                'name': 'Healthcare Invoice - Patient ID',
                'document_type': 'healthcare_invoice',
                'field_name': 'patient_id',
                'rule_type': 'regex',
                'rule_pattern': r'^PAT-\d{6,8}$',
                'description': 'Patient ID format validation'
            },
            {
                'name': 'Healthcare Invoice - Insurance Provider',
                'document_type': 'healthcare_invoice',
                'field_name': 'insurance_provider',
                'rule_type': 'enum',
                'rule_pattern': 'medicare,medicaid,blue_cross,aetna,cigna,united_healthcare,self_pay',
                'description': 'Valid insurance providers'
            },
            {
                'name': 'Healthcare Invoice - Medical Code',
                'document_type': 'healthcare_invoice',
                'field_name': 'medical_code',
                'rule_type': 'regex',
                'rule_pattern': r'^[A-Z]\d{2}\.[A-Z0-9]{1,3}$',
                'description': 'ICD-10 medical code format'
            },
            {
                'name': 'Healthcare Invoice - HIPAA Compliance',
                'document_type': 'healthcare_invoice',
                'field_name': 'hipaa_compliant',
                'rule_type': 'enum',
                'rule_pattern': 'yes,no',
                'description': 'HIPAA compliance indicator'
            },
            {
                'name': 'Healthcare Receipt - Date of Service',
                'document_type': 'healthcare_receipt',
                'field_name': 'service_date',
                'rule_type': 'date',
                'rule_pattern': '',
                'description': 'Service date validation'
            }
        ]
        
        self._create_validation_rules(healthcare_rules, overwrite)

    def setup_construction_rules(self, overwrite=False):
        """Set up validation rules for construction business"""
        self.stdout.write('Setting up construction business rules...')
        
        construction_rules = [
            {
                'name': 'Construction Invoice - Project Code',
                'document_type': 'construction_invoice',
                'field_name': 'project_code',
                'rule_type': 'regex',
                'rule_pattern': r'^PROJ-\d{4}-[A-Z]{2,4}$',
                'description': 'Project code format validation'
            },
            {
                'name': 'Construction Invoice - Safety Compliance',
                'document_type': 'construction_invoice',
                'field_name': 'safety_compliant',
                'rule_type': 'enum',
                'rule_pattern': 'yes,no',
                'description': 'Safety compliance indicator'
            },
            {
                'name': 'Construction Invoice - Material Type',
                'document_type': 'construction_invoice',
                'field_name': 'material_type',
                'rule_type': 'enum',
                'rule_pattern': 'concrete,steel,wood,electrical,plumbing,roofing,insulation,windows,doors',
                'description': 'Valid construction material types'
            },
            {
                'name': 'Construction PO - Permit Required',
                'document_type': 'construction_purchase_order',
                'field_name': 'permit_required',
                'rule_type': 'enum',
                'rule_pattern': 'yes,no',
                'description': 'Permit requirement indicator'
            },
            {
                'name': 'Construction PO - Contractor License',
                'document_type': 'construction_purchase_order',
                'field_name': 'contractor_license',
                'rule_type': 'regex',
                'rule_pattern': r'^LIC-\d{6,8}$',
                'description': 'Contractor license format validation'
            }
        ]
        
        self._create_validation_rules(construction_rules, overwrite)

    def _create_validation_rules(self, rules, overwrite=False):
        """Create validation rules from rule definitions"""
        for rule_def in rules:
            rule_name = rule_def['name']
            
            # Check if rule already exists
            existing_rule = ValidationRule.objects.filter(name=rule_name).first()
            
            if existing_rule:
                if overwrite:
                    self.stdout.write(f'  Updating existing rule: {rule_name}')
                    for key, value in rule_def.items():
                        setattr(existing_rule, key, value)
                    existing_rule.save()
                else:
                    self.stdout.write(f'  Skipping existing rule: {rule_name}')
                    continue
            else:
                self.stdout.write(f'  Creating new rule: {rule_name}')
                ValidationRule.objects.create(**rule_def)

    def _create_restaurant_workflow(self, overwrite=False):
        """Create a sample restaurant workflow"""
        workflow_name = "Restaurant Invoice Processing"
        
        # Check if workflow already exists
        existing_workflow = Workflow.objects.filter(name=workflow_name).first()
        
        if existing_workflow:
            if overwrite:
                self.stdout.write(f'  Updating existing workflow: {workflow_name}')
                existing_workflow.delete()
            else:
                self.stdout.write(f'  Skipping existing workflow: {workflow_name}')
                return
        
        # Create new workflow
        workflow = Workflow.objects.create(
            name=workflow_name,
            description="Automated processing workflow for restaurant invoices with food safety validation",
            is_active=True,
            requires_approval=True,
            approval_threshold=1000.00,
            auto_approve_below_threshold=True
        )
        
        # Create workflow steps
        steps = [
            {
                'name': 'Document Validation',
                'description': 'Validate invoice format and required fields',
                'step_order': 1,
                'step_type': 'processing'
            },
            {
                'name': 'Food Safety Check',
                'description': 'Verify food safety certification and perishable item handling',
                'step_order': 2,
                'step_type': 'processing',
                'condition_field': 'perishable_items',
                'condition_value': 'yes',
                'condition_operator': 'eq'
            },
            {
                'name': 'Manager Approval',
                'description': 'Requires manager approval for high-value invoices',
                'step_order': 3,
                'step_type': 'approval',
                'condition_field': 'total_amount',
                'condition_value': '1000',
                'condition_operator': 'gt'
            },
            {
                'name': 'Accounting System Integration',
                'description': 'Send approved invoice to accounting system',
                'step_order': 4,
                'step_type': 'integration',
                'integration_system': 'quickbooks'
            },
            {
                'name': 'Confirmation Notification',
                'description': 'Send confirmation email to supplier',
                'step_order': 5,
                'step_type': 'notification'
            }
        ]
        
        for step_def in steps:
            WorkflowStep.objects.create(workflow=workflow, **step_def)
        
        self.stdout.write(f'  Created workflow: {workflow_name} with {len(steps)} steps') 