import re
from typing import Dict, Any, List, Tuple
from asgiref.sync import sync_to_async
from ..models import ValidationRule


class ValidationEngine:
    """
    Core validation engine that applies validation rules to extracted data.
    """
    
    def __init__(self):
        self.rule_validators = {
            'regex': self._validate_regex,
            'data_type': self._validate_data_type,
            'required': self._validate_required,
            'range': self._validate_range,
            'enum': self._validate_enum,
            'cross_reference': self._validate_cross_reference,
            'calculation': self._validate_calculation,
        }
    
    async def validate_document_data(self, extracted_data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
        """
        Validates extracted document data against all applicable validation rules.
        
        Args:
            extracted_data: The extracted data from the document
            document_type: The type of document being validated
            
        Returns:
            Dict containing validation results with status, errors, and validated data
        """
        # Get all active validation rules for this document type
        @sync_to_async
        def get_validation_rules(doc_type):
            return list(ValidationRule.objects.filter(
                document_type=doc_type,
                is_active=True
            ).order_by('field_name'))
        
        validation_rules = await get_validation_rules(document_type)
        
        validation_results = {
            'status': 'passed',
            'total_rules': len(validation_rules),
            'passed_rules': 0,
            'failed_rules': 0,
            'errors': [],
            'warnings': [],
            'validated_data': extracted_data.copy(),
            'field_validations': {}
        }
        
        if not validation_rules:
            validation_results['status'] = 'no_rules'
            validation_results['warnings'].append(f"No validation rules found for document type: {document_type}")
            return validation_results
        
        # Apply each validation rule
        for rule in validation_rules:
            field_result = self._apply_validation_rule(extracted_data, rule)
            validation_results['field_validations'][rule.field_name] = field_result
            
            if field_result['passed']:
                validation_results['passed_rules'] += 1
            else:
                validation_results['failed_rules'] += 1
                validation_results['errors'].extend(field_result['errors'])
        
        # Set overall status
        if validation_results['failed_rules'] > 0:
            validation_results['status'] = 'failed'
        elif validation_results['passed_rules'] > 0:
            validation_results['status'] = 'passed'
        
        return validation_results
    
    def _apply_validation_rule(self, extracted_data: Dict[str, Any], rule: ValidationRule) -> Dict[str, Any]:
        """
        Applies a single validation rule to the extracted data.
        
        Args:
            extracted_data: The extracted data from the document
            rule: The validation rule to apply
            
        Returns:
            Dict containing the validation result for this specific rule
        """
        field_result = {
            'rule_name': rule.name,
            'field_name': rule.field_name,
            'rule_type': rule.rule_type,
            'passed': False,
            'errors': [],
            'value': None
        }
        
        # Store extracted data for cross-reference validation
        self.current_extracted_data = extracted_data
        
        # Get the field value from extracted data
        field_value = self._get_field_value(extracted_data, rule.field_name)
        field_result['value'] = field_value
        
        # Apply the appropriate validator
        validator_func = self.rule_validators.get(rule.rule_type)
        if not validator_func:
            field_result['errors'].append(f"Unknown rule type: {rule.rule_type}")
            return field_result
        
        try:
            is_valid, error_message = validator_func(field_value, rule.rule_pattern, rule)
            field_result['passed'] = is_valid
            if not is_valid and error_message:
                field_result['errors'].append(error_message)
        except Exception as e:
            field_result['errors'].append(f"Validation error for rule '{rule.name}': {str(e)}")
        
        return field_result
    
    def _get_field_value(self, extracted_data: Dict[str, Any], field_name: str) -> Any:
        """
        Extracts field value from the extracted data, handling nested fields.
        Supports both direct field access and nested field access with dot notation.
        """
        if not extracted_data:
            return None
        
        # Handle nested field names (e.g., "invoice.totalAmount")
        if '.' in field_name:
            keys = field_name.split('.')
            value = extracted_data
            for key in keys:
                if isinstance(value, dict):
                    # Handle both direct key and key with confidence structure
                    if key in value:
                        value = value[key]
                        # If value has 'value' key (confidence structure), extract it
                        if isinstance(value, dict) and 'value' in value:
                            value = value['value']
                    else:
                        return None
                else:
                    return None
            return value
        else:
            # Direct field access
            if field_name in extracted_data:
                field_data = extracted_data[field_name]
                # Handle confidence structure
                if isinstance(field_data, dict) and 'value' in field_data:
                    return field_data['value']
                return field_data
            return None
    
    def _validate_regex(self, value: Any, pattern: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value against a regular expression pattern."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for regex validation"
        
        # Convert value to string for regex validation
        str_value = str(value)
        
        try:
            if re.match(pattern, str_value):
                return True, ""
            else:
                return False, f"Field '{rule.field_name}' value '{str_value}' does not match required pattern: {pattern}"
        except re.error as e:
            return False, f"Invalid regex pattern in rule '{rule.name}': {str(e)}"
    
    def _validate_data_type(self, value: Any, expected_type: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value data type."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for data type validation"
        
        type_validators = {
            'string': lambda x: isinstance(x, str),
            'integer': lambda x: isinstance(x, int) or (isinstance(x, str) and x.isdigit()),
            'float': lambda x: isinstance(x, (int, float)) or self._is_valid_float(x),
            'number': lambda x: isinstance(x, (int, float)) or self._is_valid_number(x),
            'currency': lambda x: self._is_valid_currency(x),
            'date': lambda x: self._is_valid_date(x),
            'email': lambda x: self._is_valid_email(x),
            'phone': lambda x: self._is_valid_phone(x),
            'boolean': lambda x: isinstance(x, bool) or str(x).lower() in ['true', 'false', '1', '0']
        }
        
        validator = type_validators.get(expected_type.lower())
        if not validator:
            return False, f"Unknown data type '{expected_type}' in rule '{rule.name}'"
        
        if validator(value):
            return True, ""
        else:
            return False, f"Field '{rule.field_name}' value '{value}' is not of expected type: {expected_type}"
    
    def _validate_required(self, value: Any, pattern: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates that a required field is present and not empty."""
        if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
            return False, f"Required field '{rule.field_name}' is missing or empty"
        return True, ""
    
    def _validate_range(self, value: Any, range_spec: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value is within specified range (format: 'min,max' or 'min-max')."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for range validation"
        
        try:
            # Parse range specification (supports both 'min,max' and 'min-max' formats)
            if ',' in range_spec:
                min_val, max_val = range_spec.split(',', 1)
            elif '-' in range_spec:
                min_val, max_val = range_spec.split('-', 1)
            else:
                return False, f"Invalid range format in rule '{rule.name}'. Use 'min,max' or 'min-max'"
            
            min_val = float(min_val.strip()) if min_val.strip() else float('-inf')
            max_val = float(max_val.strip()) if max_val.strip() else float('inf')
            
            # Convert value to float for comparison
            numeric_value = float(value)
            
            if min_val <= numeric_value <= max_val:
                return True, ""
            else:
                return False, f"Field '{rule.field_name}' value {numeric_value} is outside valid range: {min_val} to {max_val}"
                
        except ValueError as e:
            return False, f"Invalid numeric value for range validation in rule '{rule.name}': {str(e)}"
    
    def _validate_enum(self, value: Any, allowed_values: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value is one of the allowed enumeration values."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for enumeration validation"
        
        # Parse allowed values (comma-separated)
        allowed_list = [v.strip() for v in allowed_values.split(',')]
        str_value = str(value).strip()
        
        if str_value in allowed_list:
            return True, ""
        else:
            return False, f"Field '{rule.field_name}' value '{str_value}' is not in allowed values: {', '.join(allowed_list)}"
    
    def _validate_cross_reference(self, value: Any, pattern: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value against a cross-reference calculation (e.g., total vs sum of line items)."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for cross-reference validation"
        
        if not rule.reference_field:
            return False, f"Cross-reference validation requires a reference_field in rule '{rule.name}'"
        
        # Get the reference field value (e.g., line items)
        reference_value = self._get_field_value(self.current_extracted_data, rule.reference_field)
        
        if reference_value is None:
            return False, f"Reference field '{rule.reference_field}' is missing for cross-reference validation"
        
        # Determine calculation type (default to sum)
        calc_type = rule.calculation_type or 'sum'
        
        try:
            # Calculate the reference value based on calculation type
            calculated_value = self._calculate_reference_value(reference_value, calc_type, rule)
            
            # Convert main value to float for comparison
            main_value = self._extract_numeric_value(value)
            
            # Compare values with tolerance
            tolerance = float(rule.tolerance) if rule.tolerance else 0.01
            difference = abs(main_value - calculated_value)
            
            if difference <= tolerance:
                return True, ""
            else:
                return False, f"Field '{rule.field_name}' value {main_value} does not match calculated {calc_type} {calculated_value} from '{rule.reference_field}' (difference: {difference}, tolerance: {tolerance})"
                
        except Exception as e:
            return False, f"Error in cross-reference validation for rule '{rule.name}': {str(e)}"
    
    def _validate_calculation(self, value: Any, pattern: str, rule: ValidationRule) -> Tuple[bool, str]:
        """Validates value against a calculation rule (similar to cross-reference but more flexible)."""
        if value is None:
            return False, f"Field '{rule.field_name}' is missing but required for calculation validation"
        
        if not rule.reference_field:
            return False, f"Calculation validation requires a reference_field in rule '{rule.name}'"
        
        # This is similar to cross-reference but allows more complex patterns
        # For now, we'll delegate to cross-reference validation
        return self._validate_cross_reference(value, pattern, rule)
    
    # Helper methods for cross-reference validation
    def _calculate_reference_value(self, reference_data: Any, calc_type: str, rule: ValidationRule) -> float:
        """Calculate the reference value based on the calculation type."""
        if not isinstance(reference_data, list):
            # If it's not a list, try to extract a single numeric value
            return self._extract_numeric_value(reference_data)
        
        # Extract numeric values from the list
        numeric_values = []
        for item in reference_data:
            if isinstance(item, dict):
                # Look for common amount/total fields in line items
                for field_name in ['amount', 'total', 'price', 'value', 'cost']:
                    if field_name in item:
                        numeric_values.append(self._extract_numeric_value(item[field_name]))
                        break
                else:
                    # If no standard fields found, look for any numeric value
                    for key, val in item.items():
                        try:
                            numeric_values.append(self._extract_numeric_value(val))
                            break
                        except:
                            continue
            else:
                # Direct numeric value
                try:
                    numeric_values.append(self._extract_numeric_value(item))
                except:
                    continue
        
        if not numeric_values:
            raise ValueError(f"No numeric values found in reference field '{rule.reference_field}'")
        
        # Perform calculation based on type
        if calc_type == 'sum':
            return sum(numeric_values)
        elif calc_type == 'average':
            return sum(numeric_values) / len(numeric_values)
        elif calc_type == 'count':
            return len(numeric_values)
        elif calc_type == 'min':
            return min(numeric_values)
        elif calc_type == 'max':
            return max(numeric_values)
        else:
            raise ValueError(f"Unknown calculation type: {calc_type}")
    
    def _extract_numeric_value(self, value: Any) -> float:
        """Extract numeric value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols and formatting
            cleaned = re.sub(r'[$€£¥₹,\s]', '', value.strip())
            try:
                return float(cleaned)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to numeric value")
        
        if isinstance(value, dict) and 'value' in value:
            return self._extract_numeric_value(value['value'])
        
        raise ValueError(f"Cannot extract numeric value from {type(value)}: {value}")
    
    # Helper methods for data type validation
    def _is_valid_float(self, value: Any) -> bool:
        """Check if value can be converted to float."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _is_valid_number(self, value: Any) -> bool:
        """Check if value is a valid number (int or float)."""
        return isinstance(value, (int, float)) or self._is_valid_float(value)
    
    def _is_valid_currency(self, value: Any) -> bool:
        """Check if value looks like a currency amount."""
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            # Remove common currency symbols and check if it's a valid number
            cleaned = re.sub(r'[$€£¥₹,\s]', '', str(value))
            return self._is_valid_float(cleaned)
        return False
    
    def _is_valid_date(self, value: Any) -> bool:
        """Check if value looks like a date."""
        if not isinstance(value, str):
            return False
        
        # Common date patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
        ]
        
        return any(re.match(pattern, str(value).strip()) for pattern in date_patterns)
    
    def _is_valid_email(self, value: Any) -> bool:
        """Check if value looks like an email address."""
        if not isinstance(value, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, str(value).strip()) is not None
    
    def _is_valid_phone(self, value: Any) -> bool:
        """Check if value looks like a phone number."""
        if not isinstance(value, str):
            return False
        
        # Remove common phone formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+\.]', '', str(value))
        # Check if remaining characters are digits and reasonable length
        return cleaned.isdigit() and 7 <= len(cleaned) <= 15


# Convenience function for external use
async def validate_document_data(extracted_data: Dict[str, Any], document_type: str) -> Dict[str, Any]:
    """
    Convenience function to validate document data using the ValidationEngine.
    
    Args:
        extracted_data: The extracted data from the document
        document_type: The type of document being validated
        
    Returns:
        Dict containing validation results
    """
    engine = ValidationEngine()
    return await engine.validate_document_data(extracted_data, document_type) 