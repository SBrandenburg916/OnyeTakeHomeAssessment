import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import spacy
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load spaCy model (install with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@dataclass
class QueryIntent:
    action: str  # "find", "show", "get", etc.
    resource_type: str  # "patients", "conditions", etc.
    conditions: List[Dict[str, Any]]
    age_filter: Optional[Dict[str, Any]] = None
    count_limit: Optional[int] = None

class FHIRNLPProcessor:
    def __init__(self):
        self.condition_mappings = {
            "diabetes": {"code": "E11", "display": "Type 2 diabetes mellitus", "system": "http://hl7.org/fhir/sid/icd-10"},
            "diabetic": {"code": "E11", "display": "Type 2 diabetes mellitus", "system": "http://hl7.org/fhir/sid/icd-10"},
            "hypertension": {"code": "I10", "display": "Essential hypertension", "system": "http://hl7.org/fhir/sid/icd-10"},
            "high blood pressure": {"code": "I10", "display": "Essential hypertension", "system": "http://hl7.org/fhir/sid/icd-10"},
            "heart disease": {"code": "I25", "display": "Chronic ischemic heart disease", "system": "http://hl7.org/fhir/sid/icd-10"},
            "asthma": {"code": "J45", "display": "Asthma", "system": "http://hl7.org/fhir/sid/icd-10"},
            "cancer": {"code": "C80", "display": "Malignant neoplasm", "system": "http://hl7.org/fhir/sid/icd-10"},
            "depression": {"code": "F32", "display": "Major depressive disorder", "system": "http://hl7.org/fhir/sid/icd-10"}
        }
        
        self.age_patterns = [
            (r"over (\d+)", "gt"),
            (r"above (\d+)", "gt"),
            (r"under (\d+)", "lt"),
            (r"below (\d+)", "lt"),
            (r"between (\d+) and (\d+)", "range"),
            (r"(\d+) to (\d+)", "range")
        ]
    
    def extract_intent(self, query: str) -> QueryIntent:
        query_lower = query.lower()
        
        # Extract action
        action = "find"
        if any(word in query_lower for word in ["show", "display", "list"]):
            action = "show"
        elif any(word in query_lower for word in ["get", "retrieve", "fetch"]):
            action = "get"
        elif any(word in query_lower for word in ["count", "how many"]):
            action = "count"
        
        # Extract resource type
        resource_type = "Patient"
        if "patient" in query_lower:
            resource_type = "Patient"
        
        # Extract conditions
        conditions = []
        for condition_text, condition_data in self.condition_mappings.items():
            if condition_text in query_lower:
                conditions.append(condition_data)
        
        # Extract age filters
        age_filter = None
        for pattern, filter_type in self.age_patterns:
            match = re.search(pattern, query_lower)
            if match:
                if filter_type == "range":
                    age_filter = {
                        "type": "range",
                        "min": int(match.group(1)),
                        "max": int(match.group(2))
                    }
                else:
                    age_filter = {
                        "type": filter_type,
                        "value": int(match.group(1))
                    }
                break
        
        # Extract count limit
        count_limit = None
        count_match = re.search(r"(\d+)\s+patients", query_lower)
        if count_match:
            count_limit = int(count_match.group(1))
        
        return QueryIntent(
            action=action,
            resource_type=resource_type,
            conditions=conditions,
            age_filter=age_filter,
            count_limit=count_limit
        )
    
    def build_fhir_query(self, intent: QueryIntent) -> Dict[str, Any]:
        """Convert intent to FHIR API query parameters"""
        query_params = {
            "resourceType": intent.resource_type
        }
        
        # Add condition filters
        if intent.conditions:
            condition_codes = [f"{cond['system']}|{cond['code']}" for cond in intent.conditions]
            query_params["condition"] = ",".join(condition_codes)
        
        # Add age filters
        if intent.age_filter:
            if intent.age_filter["type"] == "gt":
                query_params["birthdate"] = f"le{(datetime.now() - timedelta(days=365*intent.age_filter['value'])).strftime('%Y-%m-%d')}"
            elif intent.age_filter["type"] == "lt":
                query_params["birthdate"] = f"ge{(datetime.now() - timedelta(days=365*intent.age_filter['value'])).strftime('%Y-%m-%d')}"
            elif intent.age_filter["type"] == "range":
                min_date = (datetime.now() - timedelta(days=365*intent.age_filter['max'])).strftime('%Y-%m-%d')
                max_date = (datetime.now() - timedelta(days=365*intent.age_filter['min'])).strftime('%Y-%m-%d')
                query_params["birthdate"] = f"ge{min_date}&birthdate=le{max_date}"
        
        # Add count limit
        if intent.count_limit:
            query_params["_count"] = intent.count_limit
        
        return query_params
    
    def generate_mock_fhir_response(self, intent: QueryIntent) -> Dict[str, Any]:
        """Generate mock FHIR Bundle response based on query intent"""
        patients = []
        
        # Generate mock patients based on conditions and filters
        base_patients = [
            {"id": "1", "name": "John Doe", "birthDate": "1970-05-15", "gender": "male"},
            {"id": "2", "name": "Jane Smith", "birthDate": "1965-08-22", "gender": "female"},
            {"id": "3", "name": "Robert Johnson", "birthDate": "1980-12-03", "gender": "male"},
            {"id": "4", "name": "Mary Williams", "birthDate": "1955-03-10", "gender": "female"},
            {"id": "5", "name": "David Brown", "birthDate": "1975-11-28", "gender": "male"},
        ]
        
        for patient in base_patients:
            # Calculate age
            birth_year = int(patient["birthDate"][:4])
            age = 2025 - birth_year
            
            # Apply age filter
            if intent.age_filter:
                if intent.age_filter["type"] == "gt" and age <= intent.age_filter["value"]:
                    continue
                elif intent.age_filter["type"] == "lt" and age >= intent.age_filter["value"]:
                    continue
                elif intent.age_filter["type"] == "range":
                    if age < intent.age_filter["min"] or age > intent.age_filter["max"]:
                        continue
            
            # Add conditions if specified
            conditions = []
            if intent.conditions:
                for condition in intent.conditions:
                    conditions.append({
                        "code": {
                            "coding": [{
                                "system": condition["system"],
                                "code": condition["code"],
                                "display": condition["display"]
                            }]
                        },
                        "subject": {"reference": f"Patient/{patient['id']}"}
                    })
            
            patient_resource = {
                "resourceType": "Patient",
                "id": patient["id"],
                "name": [{"given": [patient["name"].split()[0]], "family": patient["name"].split()[1]}],
                "birthDate": patient["birthDate"],
                "gender": patient["gender"],
                "conditions": conditions,
                "age": age
            }
            
            patients.append(patient_resource)
            
            # Apply count limit
            if intent.count_limit and len(patients) >= intent.count_limit:
                break
        
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(patients),
            "entry": [{"resource": patient} for patient in patients]
        }

# Initialize processor
processor = FHIRNLPProcessor()

@app.route('/query', methods=['POST'])
def process_query():
    data = request.get_json()
    query_text = data.get('query', '')
    
    if not query_text:
        return jsonify({"error": "Query text is required"}), 400
    
    try:
        # Extract intent
        intent = processor.extract_intent(query_text)
        
        # Build FHIR query
        fhir_query = processor.build_fhir_query(intent)
        
        # Generate mock response
        mock_response = processor.generate_mock_fhir_response(intent)
        
        return jsonify({
            "original_query": query_text,
            "extracted_intent": {
                "action": intent.action,
                "resource_type": intent.resource_type,
                "conditions": intent.conditions,
                "age_filter": intent.age_filter,
                "count_limit": intent.count_limit
            },
            "fhir_query_params": fhir_query,
            "mock_fhir_response": mock_response
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "FHIR NLP Processor"})

if __name__ == '__main__':
    # Example usage
    test_queries = [
        "Show me all diabetic patients over 50",
        "Find patients with hypertension under 65",
        "Get all patients with heart disease between 40 and 70",
        "How many patients have asthma?",
        "List 3 patients with depression"
    ]
    
    print("Testing NLP to FHIR conversion:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        intent = processor.extract_intent(query)
        fhir_query = processor.build_fhir_query(intent)
        mock_response = processor.generate_mock_fhir_response(intent)
        
        print(f"Intent: {intent}")
        print(f"FHIR Query: {fhir_query}")
        print(f"Results: {mock_response['total']} patients found")
    
    print("\nStarting Flask server...")
    app.run(debug=True, port=5000)