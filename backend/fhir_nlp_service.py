#!/usr/bin/env python3
"""
FHIR NLP Service - Backend for AI on FHIR Take-Home Assessment
Processes natural language queries and converts them to FHIR API requests
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@dataclass
class QueryIntent:
    """Represents extracted intent from natural language query"""
    action: str  # 'find', 'show', 'get', 'list'
    resource_type: str  # 'patients', 'conditions', 'observations'
    filters: Dict[str, Any]  # age, gender, condition, etc.
    modifiers: List[str]  # 'all', 'recent', 'active'

class FHIRNLPProcessor:
    """Processes natural language queries into FHIR requests"""
    
    def __init__(self):
        self.condition_mappings = {
            'diabetes': 'E11.9',
            'diabetic': 'E11.9',
            'hypertension': 'I10',
            'high blood pressure': 'I10',
            'depression': 'F32.9',
            'heart disease': 'I25.9',
            'asthma': 'J45.9',
            'copd': 'J44.1',
            'chronic obstructive pulmonary disease': 'J44.1'
        }
        
        self.action_patterns = {
            r'\b(show|display|list|get)\b': 'show',
            r'\b(find|search|locate)\b': 'find',
            r'\b(count|how many)\b': 'count'
        }
        
        self.resource_patterns = {
            r'\bpatients?\b': 'Patient',
            r'\bconditions?\b': 'Condition',
            r'\bobservations?\b': 'Observation'
        }
    
    def extract_intent(self, query: str) -> QueryIntent:
        """Extract intent and entities from natural language query"""
        query_lower = query.lower()
        
        # Extract action
        action = 'show'  # default
        for pattern, action_type in self.action_patterns.items():
            if re.search(pattern, query_lower):
                action = action_type
                break
        
        # Extract resource type
        resource_type = 'Patient'  # default
        for pattern, resource in self.resource_patterns.items():
            if re.search(pattern, query_lower):
                resource_type = resource
                break
        
        # Extract filters
        filters = {}
        modifiers = []
        
        # Age filters
        age_match = re.search(r'\b(over|above|older than|greater than)\s+(\d+)\b', query_lower)
        if age_match:
            filters['age'] = {'operator': '>', 'value': int(age_match.group(2))}
        
        age_match = re.search(r'\b(under|below|younger than|less than)\s+(\d+)\b', query_lower)
        if age_match:
            filters['age'] = {'operator': '<', 'value': int(age_match.group(2))}
        
        age_match = re.search(r'\bage\s+(\d+)\b', query_lower)
        if age_match:
            filters['age'] = {'operator': '=', 'value': int(age_match.group(1))}
        
        # Gender filters
        if re.search(r'\b(male|men)\b', query_lower):
            filters['gender'] = 'male'
        elif re.search(r'\b(female|women)\b', query_lower):
            filters['gender'] = 'female'
        
        # Condition filters
        for condition, code in self.condition_mappings.items():
            if condition in query_lower:
                filters['condition'] = {'name': condition, 'code': code}
                break
        
        # Modifiers
        if re.search(r'\ball\b', query_lower):
            modifiers.append('all')
        if re.search(r'\bactive\b', query_lower):
            modifiers.append('active')
        if re.search(r'\brecent\b', query_lower):
            modifiers.append('recent')
        
        return QueryIntent(action, resource_type, filters, modifiers)
    
    def build_fhir_query(self, intent: QueryIntent) -> Dict[str, Any]:
        """Convert intent to FHIR API query parameters"""
        query_params = {}
        
        # Base resource
        query_params['resourceType'] = intent.resource_type
        
        # Age filters
        if 'age' in intent.filters:
            age_filter = intent.filters['age']
            current_year = datetime.now().year
            birth_year = current_year - age_filter['value']
            
            if age_filter['operator'] == '>':
                query_params['birthdate'] = f'lt{birth_year}-01-01'
            elif age_filter['operator'] == '<':
                query_params['birthdate'] = f'gt{birth_year}-01-01'
            else:
                query_params['birthdate'] = f'ge{birth_year}-01-01&birthdate=lt{birth_year+1}-01-01'
        
        # Gender filters
        if 'gender' in intent.filters:
            query_params['gender'] = intent.filters['gender']
        
        # Condition filters
        if 'condition' in intent.filters:
            condition = intent.filters['condition']
            if intent.resource_type == 'Patient':
                query_params['_has:Condition:patient:code'] = condition['code']
            elif intent.resource_type == 'Condition':
                query_params['code'] = condition['code']
        
        # Modifiers
        if 'active' in intent.modifiers:
            query_params['clinical-status'] = 'active'
        
        if 'recent' in intent.modifiers:
            recent_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            query_params['date'] = f'ge{recent_date}'
        
        return query_params
    
    def generate_mock_fhir_response(self, intent: QueryIntent, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock FHIR response based on query"""
        
        # Generate mock patients
        mock_patients = []
        num_patients = random.randint(5, 15)
        
        for i in range(num_patients):
            age = random.randint(25, 85)
            gender = random.choice(['male', 'female'])
            
            # Apply filters
            if 'age' in intent.filters:
                age_filter = intent.filters['age']
                if age_filter['operator'] == '>' and age <= age_filter['value']:
                    continue
                elif age_filter['operator'] == '<' and age >= age_filter['value']:
                    continue
                elif age_filter['operator'] == '=' and age != age_filter['value']:
                    continue
            
            if 'gender' in intent.filters and gender != intent.filters['gender']:
                continue
            
            patient = {
                'resourceType': 'Patient',
                'id': f'patient-{i+1}',
                'name': [{
                    'use': 'official',
                    'family': random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']),
                    'given': [random.choice(['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Chris', 'Amanda', 'Robert', 'Jennifer'])]
                }],
                'gender': gender,
                'birthDate': f'{datetime.now().year - age}-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                'age': age
            }
            
            if 'condition' in intent.filters:
                condition = intent.filters['condition']
                patient['conditions'] = [{
                    'code': condition['code'],
                    'display': condition['name'].title()
                }]
            
            mock_patients.append(patient)
        
        return {
            'resourceType': 'Bundle',
            'type': 'searchset',
            'total': len(mock_patients),
            'entry': [{'resource': patient} for patient in mock_patients]
        }

# Initialize processor
processor = FHIRNLPProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/query', methods=['POST'])
def process_query():
    """Process natural language query and return FHIR response"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query']
        
        # Extract intent
        intent = processor.extract_intent(query)
        
        # Build FHIR query
        fhir_query = processor.build_fhir_query(intent)
        
        # Generate mock response
        mock_response = processor.generate_mock_fhir_response(intent, fhir_query)
        
        return jsonify({
            'original_query': query,
            'extracted_intent': {
                'action': intent.action,
                'resource_type': intent.resource_type,
                'filters': intent.filters,
                'modifiers': intent.modifiers
            },
            'fhir_query': fhir_query,
            'fhir_response': mock_response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/examples', methods=['GET'])
def get_examples():
    """Get example queries for testing"""
    examples = [
        "Show me all diabetic patients over 50",
        "Find female patients with hypertension",
        "List patients under 30 with depression",
        "Show male patients with heart disease over 65",
        "Get all active asthma patients"
    ]
    return jsonify({'examples': examples})

if __name__ == '__main__':
    print("Starting FHIR NLP Service...")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /query - Process natural language query")
    print("  GET  /examples - Get example queries")
    print()
    
    # Test with example queries
    print("Testing with example queries:")
    test_queries = [
        "Show me all diabetic patients over 50",
        "Find female patients with hypertension",
        "List patients under 30"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        intent = processor.extract_intent(query)
        fhir_query = processor.build_fhir_query(intent)
        print(f"Intent: {intent}")
        print(f"FHIR Query: {fhir_query}")
    
    app.run(debug=True, host='0.0.0.0', port=5050)