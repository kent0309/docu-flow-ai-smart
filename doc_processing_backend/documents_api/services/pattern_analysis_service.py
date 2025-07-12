import re
import json
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter
from decimal import Decimal
from datetime import datetime
from asgiref.sync import sync_to_async
from ..models import Document, ValidationRule
import statistics


class PatternAnalysisService:
    """
    Service for analyzing document patterns and automatically creating validation rules.
    """
    
    def __init__(self):
        self.pattern_analyzers = {
            'data_type': self._analyze_data_type_patterns,
            'regex': self._analyze_regex_patterns,
            'range': self._analyze_range_patterns,
            'enum': self._analyze_enum_patterns,
            'cross_reference': self._analyze_cross_reference_patterns,
        }
    
    async def analyze_document_patterns(self, document_type: str, min_samples: int = 5) -> Dict[str, Any]:
        """
        Analyze patterns in documents of a specific type and suggest validation rules.
        
        Args:
            document_type: The type of document to analyze
            min_samples: Minimum number of documents required for pattern analysis
            
        Returns:
            Dict containing suggested validation rules and analysis results
        """
        # Get processed documents of the specified type
        @sync_to_async
        def get_documents(doc_type):
            return list(Document.objects.filter(
                document_type=doc_type,
                status='processed',
                extracted_data__isnull=False
            ).values('id', 'extracted_data', 'filename'))
        
        documents = await get_documents(document_type)
        
        if len(documents) < min_samples:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least {min_samples} processed documents, found {len(documents)}',
                'suggested_rules': []
            }
        
        # Extract field data from all documents
        field_data = self._extract_field_data(documents)
        
        # Analyze patterns for each field
        suggested_rules = []
        analysis_results = {}
        
        for field_name, field_values in field_data.items():
            field_analysis = self._analyze_field_patterns(field_name, field_values, document_type)
            analysis_results[field_name] = field_analysis
            
            # Generate suggested rules based on analysis
            for rule_type, patterns in field_analysis.items():
                if patterns.get('confidence', 0) >= 0.8:  # High confidence threshold
                    suggested_rule = self._create_rule_suggestion(
                        field_name, rule_type, patterns, document_type
                    )
                    if suggested_rule:
                        suggested_rules.append(suggested_rule)
        
        return {
            'status': 'success',
            'document_type': document_type,
            'analyzed_documents': len(documents),
            'analysis_results': analysis_results,
            'suggested_rules': suggested_rules
        }
    
    async def auto_create_validation_rules(self, document_type: str, confidence_threshold: float = 0.9) -> Dict[str, Any]:
        """
        Automatically create validation rules based on pattern analysis.
        
        Args:
            document_type: The type of document to analyze
            confidence_threshold: Minimum confidence level for auto-creation
            
        Returns:
            Dict containing created rules and results
        """
        # First, analyze patterns
        analysis = await self.analyze_document_patterns(document_type)
        
        if analysis['status'] != 'success':
            return analysis
        
        # Filter rules by confidence threshold
        high_confidence_rules = [
            rule for rule in analysis['suggested_rules']
            if rule.get('confidence', 0) >= confidence_threshold
        ]
        
        if not high_confidence_rules:
            return {
                'status': 'no_high_confidence_rules',
                'message': f'No rules met confidence threshold of {confidence_threshold}',
                'analyzed_rules': len(analysis['suggested_rules']),
                'created_rules': []
            }
        
        # Create validation rules
        created_rules = []
        
        @sync_to_async
        def create_rule(rule_data):
            # Check if rule already exists
            existing_rule = ValidationRule.objects.filter(
                document_type=rule_data['document_type'],
                field_name=rule_data['field_name'],
                rule_type=rule_data['rule_type']
            ).first()
            
            if existing_rule:
                return None
            
            # Create new rule
            new_rule = ValidationRule.objects.create(
                name=rule_data['name'],
                document_type=rule_data['document_type'],
                field_name=rule_data['field_name'],
                rule_type=rule_data['rule_type'],
                rule_pattern=rule_data['rule_pattern'],
                description=rule_data['description'],
                reference_field=rule_data.get('reference_field'),
                calculation_type=rule_data.get('calculation_type'),
                tolerance=rule_data.get('tolerance'),
                auto_created=True,
                is_active=True
            )
            return new_rule
        
        for rule_data in high_confidence_rules:
            created_rule = await create_rule(rule_data)
            if created_rule:
                created_rules.append({
                    'id': str(created_rule.id),
                    'name': created_rule.name,
                    'field_name': created_rule.field_name,
                    'rule_type': created_rule.rule_type,
                    'confidence': rule_data.get('confidence', 0)
                })
        
        return {
            'status': 'success',
            'document_type': document_type,
            'analyzed_rules': len(analysis['suggested_rules']),
            'created_rules': created_rules,
            'total_created': len(created_rules)
        }
    
    def _extract_field_data(self, documents: List[Dict]) -> Dict[str, List[Any]]:
        """Extract field data from documents for pattern analysis."""
        field_data = defaultdict(list)
        
        for doc in documents:
            extracted_data = doc.get('extracted_data', {})
            if not extracted_data:
                continue
            
            # Flatten nested data structure
            flattened_data = self._flatten_dict(extracted_data)
            
            for field_name, value in flattened_data.items():
                # Skip validation results and metadata
                if field_name.startswith('validation_') or field_name in ['raw_text', 'extraction_time']:
                    continue
                
                field_data[field_name].append(value)
        
        return field_data
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Flatten nested dictionary structure."""
        flattened = {}
        
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                if 'value' in value:
                    # Handle confidence structure
                    flattened[full_key] = value['value']
                else:
                    # Recursively flatten nested dicts
                    flattened.update(self._flatten_dict(value, full_key))
            else:
                flattened[full_key] = value
        
        return flattened
    
    def _analyze_field_patterns(self, field_name: str, field_values: List[Any], document_type: str) -> Dict[str, Any]:
        """Analyze patterns in a specific field."""
        analysis = {}
        
        # Remove None values and empty strings
        clean_values = [v for v in field_values if v is not None and v != '']
        
        if not clean_values:
            return analysis
        
        # Analyze each pattern type
        for pattern_type, analyzer_func in self.pattern_analyzers.items():
            try:
                pattern_analysis = analyzer_func(field_name, clean_values, document_type)
                if pattern_analysis:
                    analysis[pattern_type] = pattern_analysis
            except Exception as e:
                # Log error but continue with other analyzers
                print(f"Error analyzing {pattern_type} patterns for field {field_name}: {str(e)}")
        
        return analysis
    
    def _analyze_data_type_patterns(self, field_name: str, values: List[Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Analyze data type patterns in field values."""
        type_counts = Counter()
        
        for value in values:
            if isinstance(value, str):
                # Check for specific string patterns
                if re.match(r'^\d+$', value):
                    type_counts['integer'] += 1
                elif re.match(r'^\d*\.\d+$', value):
                    type_counts['float'] += 1
                elif self._is_currency_string(value):
                    type_counts['currency'] += 1
                elif self._is_date_string(value):
                    type_counts['date'] += 1
                elif self._is_email_string(value):
                    type_counts['email'] += 1
                elif self._is_phone_string(value):
                    type_counts['phone'] += 1
                else:
                    type_counts['string'] += 1
            elif isinstance(value, int):
                type_counts['integer'] += 1
            elif isinstance(value, float):
                type_counts['float'] += 1
            elif isinstance(value, bool):
                type_counts['boolean'] += 1
            else:
                type_counts['unknown'] += 1
        
        if not type_counts:
            return None
        
        # Determine most common type
        most_common_type, count = type_counts.most_common(1)[0]
        confidence = count / len(values)
        
        if confidence >= 0.7:  # At least 70% of values match the type
            return {
                'type': most_common_type,
                'confidence': confidence,
                'sample_count': len(values),
                'type_distribution': dict(type_counts)
            }
        
        return None
    
    def _analyze_regex_patterns(self, field_name: str, values: List[Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Analyze regex patterns in field values."""
        # Convert all values to strings
        str_values = [str(v) for v in values]
        
        # Common patterns to check
        patterns = [
            (r'^[A-Z]{2,3}-\d{4,}$', 'invoice_number'),
            (r'^INV-\d{4,}$', 'invoice_number_inv'),
            (r'^[A-Z]{2}\d{6}$', 'reference_code'),
            (r'^\d{4}-\d{2}-\d{2}$', 'date_iso'),
            (r'^\d{2}/\d{2}/\d{4}$', 'date_us'),
            (r'^[+]?[\d\s\-\(\)]+$', 'phone'),
            (r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', 'email'),
        ]
        
        best_pattern = None
        best_confidence = 0
        
        for pattern, pattern_name in patterns:
            matches = sum(1 for value in str_values if re.match(pattern, value))
            confidence = matches / len(str_values)
            
            if confidence > best_confidence and confidence >= 0.8:
                best_confidence = confidence
                best_pattern = {
                    'pattern': pattern,
                    'name': pattern_name,
                    'confidence': confidence,
                    'matches': matches,
                    'total': len(str_values)
                }
        
        return best_pattern
    
    def _analyze_range_patterns(self, field_name: str, values: List[Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Analyze numeric range patterns."""
        # Extract numeric values
        numeric_values = []
        for value in values:
            try:
                if isinstance(value, (int, float)):
                    numeric_values.append(float(value))
                elif isinstance(value, str):
                    # Try to extract numeric value from string
                    cleaned = re.sub(r'[^\d.-]', '', value)
                    if cleaned:
                        numeric_values.append(float(cleaned))
            except:
                continue
        
        if len(numeric_values) < 3:  # Need at least 3 values for range analysis
            return None
        
        # Calculate statistics
        min_val = min(numeric_values)
        max_val = max(numeric_values)
        mean_val = statistics.mean(numeric_values)
        std_dev = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
        
        # Define reasonable range (mean ± 2 standard deviations)
        range_min = max(min_val, mean_val - 2 * std_dev)
        range_max = min(max_val, mean_val + 2 * std_dev)
        
        # Check how many values fall within this range
        values_in_range = sum(1 for v in numeric_values if range_min <= v <= range_max)
        confidence = values_in_range / len(numeric_values)
        
        if confidence >= 0.8:
            return {
                'min': range_min,
                'max': range_max,
                'confidence': confidence,
                'sample_count': len(numeric_values),
                'statistics': {
                    'min': min_val,
                    'max': max_val,
                    'mean': mean_val,
                    'std_dev': std_dev
                }
            }
        
        return None
    
    def _analyze_enum_patterns(self, field_name: str, values: List[Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Analyze enumeration patterns (limited set of values)."""
        # Count unique values
        value_counts = Counter(str(v) for v in values)
        unique_values = list(value_counts.keys())
        
        # Check if it's a good candidate for enumeration
        total_values = len(values)
        unique_count = len(unique_values)
        
        # Good enumeration candidates:
        # - Small number of unique values relative to total
        # - Each unique value appears multiple times
        if unique_count <= 10 and unique_count < total_values * 0.3:
            # Check if each value appears at least twice
            min_occurrences = min(value_counts.values())
            if min_occurrences >= 2:
                confidence = 1.0 - (unique_count / total_values)
                return {
                    'values': unique_values,
                    'confidence': confidence,
                    'unique_count': unique_count,
                    'total_values': total_values,
                    'value_distribution': dict(value_counts)
                }
        
        return None
    
    def _analyze_cross_reference_patterns(self, field_name: str, values: List[Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Analyze cross-reference patterns (e.g., totals vs line items)."""
        # This is more complex and requires analyzing the full document structure
        # For now, we'll return None and implement this in a future enhancement
        return None
    
    def _create_rule_suggestion(self, field_name: str, rule_type: str, patterns: Dict[str, Any], document_type: str) -> Optional[Dict[str, Any]]:
        """Create a validation rule suggestion based on pattern analysis."""
        base_rule = {
            'field_name': field_name,
            'rule_type': rule_type,
            'document_type': document_type,
            'confidence': patterns.get('confidence', 0),
            'description': f'Auto-generated {rule_type} rule for {field_name} based on pattern analysis',
            'auto_created': True
        }
        
        if rule_type == 'data_type':
            base_rule.update({
                'name': f'{field_name}_type_check',
                'rule_pattern': patterns['type'],
                'description': f'Validates that {field_name} is of type {patterns["type"]} (confidence: {patterns["confidence"]:.2f})'
            })
        
        elif rule_type == 'regex':
            base_rule.update({
                'name': f'{field_name}_format_check',
                'rule_pattern': patterns['pattern'],
                'description': f'Validates {field_name} format as {patterns["name"]} (confidence: {patterns["confidence"]:.2f})'
            })
        
        elif rule_type == 'range':
            base_rule.update({
                'name': f'{field_name}_range_check',
                'rule_pattern': f'{patterns["min"]:.2f},{patterns["max"]:.2f}',
                'description': f'Validates {field_name} is within range {patterns["min"]:.2f} to {patterns["max"]:.2f} (confidence: {patterns["confidence"]:.2f})'
            })
        
        elif rule_type == 'enum':
            base_rule.update({
                'name': f'{field_name}_enum_check',
                'rule_pattern': ','.join(patterns['values']),
                'description': f'Validates {field_name} is one of: {", ".join(patterns["values"][:5])}{"..." if len(patterns["values"]) > 5 else ""} (confidence: {patterns["confidence"]:.2f})'
            })
        
        else:
            return None
        
        return base_rule
    
    # Helper methods
    def _is_currency_string(self, value: str) -> bool:
        """Check if string represents a currency value."""
        pattern = r'^[\$€£¥₹]?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?$'
        return bool(re.match(pattern, value.strip()))
    
    def _is_date_string(self, value: str) -> bool:
        """Check if string represents a date."""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}/\d{2}/\d{4}$',
            r'^\d{2}-\d{2}-\d{4}$',
            r'^\d{1,2}/\d{1,2}/\d{4}$'
        ]
        return any(re.match(pattern, value.strip()) for pattern in date_patterns)
    
    def _is_email_string(self, value: str) -> bool:
        """Check if string represents an email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value.strip()))
    
    def _is_phone_string(self, value: str) -> bool:
        """Check if string represents a phone number."""
        cleaned = re.sub(r'[\s\-\(\)\+\.]', '', value)
        return cleaned.isdigit() and 7 <= len(cleaned) <= 15


# Convenience functions for external use
async def analyze_document_patterns(document_type: str, min_samples: int = 5) -> Dict[str, Any]:
    """Analyze patterns in documents and suggest validation rules."""
    service = PatternAnalysisService()
    return await service.analyze_document_patterns(document_type, min_samples)


async def auto_create_validation_rules(document_type: str, confidence_threshold: float = 0.9) -> Dict[str, Any]:
    """Automatically create validation rules based on pattern analysis."""
    service = PatternAnalysisService()
    return await service.auto_create_validation_rules(document_type, confidence_threshold) 