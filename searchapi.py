import os
import requests
import base64
import json

# Azure DevOps Organization Name
ORG_NAME = "your-organization"

# Read PAT from Environment Variable
PAT = os.getenv("TOKEN")
if not PAT:
    raise ValueError("PAT is not set. Ensure 'TOKEN' is declared in the ADO pipeline environment.")

# Search Term
SEARCH_TERM = "your-search-text"

# API URL
API_URL = f"https://almsearch.dev.azure.com/{ORG_NAME}/_apis/search/codesearchresults?api-version=7.1-preview.1"

# Authentication (Base64 encode the PAT)
auth_header = base64.b64encode(f":{PAT}".encode()).decode()

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_header}"
}

# Request body with $top parameter
payload = {
    "searchText": SEARCH_TERM,
    "$top": 100  # Adjust based on your needs (Max: 1000)
}

# Make API request
response = requests.post(API_URL, json=payload, headers=headers)

# Print raw response (for debugging)
print("Raw Response Status Code:", response.status_code)
print("Raw Response Text:", response.text)

# Check if response is JSON before parsing
try:
    results = response.json()
    print("Parsed JSON Response:", json.dumps(results, indent=4))  # Pretty print JSON
except requests.exceptions.JSONDecodeError:
    print(f"Error: API returned non-JSON response: {response.text}")
    exit(1)

# Validate response structure
if "results" not in results:
    print(f"Unexpected API response structure: {results}")
    exit(1)