# AI-Powered FHIR Query Backend

This Python-based service accepts natural language queries and simulates corresponding FHIR API requests. It demonstrates how AI can be used to convert human-readable healthcare requests into machine-readable formats using FHIR standards.

## Features

- Parses natural language queries using spaCy
- Extracts medical entities and patient criteria
- Simulates FHIR queries using the Patient and Condition resources
- Outputs example mappings for review

## Example Queries

| Input Query                                 | Simulated FHIR API Endpoint Example |
|--------------------------------------------|--------------------------------------|
| Show me all diabetic patients over 50      | `/Patient?age=gt50&condition=diabetes` |
| List patients with asthma under 18         | `/Patient?age=lt18&condition=asthma` |
| Find female patients with hypertension     | `/Patient?gender=female&condition=hypertension` |

## Setup Instructions

1. **Install dependencies**
   pip install -r requirements.txt

2. **Download spaCy’s English language model**
   python -m spacy download en_core_web_sm

3. **Rerun the backend**
   python fhir_nlp_service.py

4. **Install flask-cors**
   pip install flask-cors

5. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


