#!/usr/bin/env python
"""
Test script for business rules functionality
"""

import os
import django
import asyncio
import json
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doc_processing_project.settings')
django.setup()

from documents_api.services.business_rules_service import (
    BusinessRulesService,
    get_available_business_types,
    get_business_type_configuration,
    validate_document_with_business_rules
)

async def test_business_rules():
    """Test the business rules functionality"""
    print("🧪 Testing Business Rules System\n")
    
    # Test 1: Get available business types
    print("1. Testing available business types:")
    try:
        business_types = await get_available_business_types()
        print(f"   ✅ Found {len(business_types)} business types:")
        for bt, config in business_types.items():
            print(f"      - {config['name']}: {config['validation_rules_count']} rules, {config['integration_templates_count']} integrations")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Get restaurant configuration
    print("2. Testing restaurant configuration:")
    try:
        restaurant_config = await get_business_type_configuration('restaurant')
        print(f"   ✅ Restaurant configuration loaded:")
        print(f"      - Rules: {len(restaurant_config['validation_rules'])}")
        print(f"      - Workflows: {len(restaurant_config['workflows'])}")
        print(f"      - Integrations: {len(restaurant_config['integration_templates'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Validate a restaurant invoice
    print("3. Testing restaurant invoice validation:")
    try:
        # Sample restaurant invoice data
        restaurant_invoice_data = {
            'supplier_name': 'ABC Food Supply',
            'food_safety_cert': 'FS-2024-1234',
            'perishable_items': 'yes',
            'total_amount': 1250.50,
            'line_items': [
                {'item': 'Fresh Beef', 'quantity': 50, 'price': 15.00, 'amount': 750.00},
                {'item': 'Chicken Breast', 'quantity': 30, 'price': 12.50, 'amount': 375.00},
                {'item': 'Vegetables', 'quantity': 25, 'price': 5.00, 'amount': 125.00}
            ],
            'delivery_date': '2024-01-15',
            'priority': 'high'
        }
        
        validation_result = await validate_document_with_business_rules(
            restaurant_invoice_data, 
            'restaurant_invoice'
        )
        
        print(f"   ✅ Validation completed:")
        print(f"      - Status: {validation_result['status']}")
        print(f"      - Business Type: {validation_result.get('business_type', 'N/A')}")
        print(f"      - Rules Applied: {validation_result.get('total_rules', 0)}")
        print(f"      - Passed: {validation_result.get('passed_rules', 0)}")
        print(f"      - Failed: {validation_result.get('failed_rules', 0)}")
        
        if validation_result.get('errors'):
            print(f"      - Errors: {validation_result['errors']}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Test with invalid data
    print("4. Testing validation with invalid data:")
    try:
        invalid_data = {
            'supplier_name': '',  # Required field missing
            'food_safety_cert': 'invalid-format',  # Wrong format
            'perishable_items': 'maybe',  # Invalid enum value
            'total_amount': 75000,  # Above range
            'line_items': []  # Empty
        }
        
        validation_result = await validate_document_with_business_rules(
            invalid_data, 
            'restaurant_invoice'
        )
        
        print(f"   ✅ Invalid data validation completed:")
        print(f"      - Status: {validation_result['status']}")
        print(f"      - Failed Rules: {validation_result.get('failed_rules', 0)}")
        print(f"      - Errors: {len(validation_result.get('errors', []))}")
        
        if validation_result.get('errors'):
            print("      - Error details:")
            for error in validation_result['errors'][:3]:  # Show first 3 errors
                print(f"        • {error}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 5: Test service methods
    print("5. Testing service methods:")
    try:
        service = BusinessRulesService()
        
        # Test get recommended integrations
        integrations = await service.get_recommended_integrations('restaurant')
        print(f"   ✅ Found {len(integrations)} recommended integrations for restaurant")
        
        # Test document type rules
        rules = await service.get_document_type_rules('restaurant_invoice')
        print(f"   ✅ Found {len(rules)} rules for restaurant_invoice document type")
        
        # Test activate/deactivate
        activate_result = await service.activate_business_type_rules('restaurant')
        print(f"   ✅ Activation result: {activate_result['status']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 Business Rules Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_business_rules()) 