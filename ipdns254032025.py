import os
import requests
import base64
import csv
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
    "$top": 100
}

# Make API request
response = requests.post(API_URL, json=payload, headers=headers)

# Check response
try:
    results = response.json()
    print("Full JSON Response:\n", json.dumps(results, indent=4))  # Pretty print JSON
except requests.exceptions.JSONDecodeError:
    print(f"Error: API returned non-JSON response: {response.text}")
    exit(1)

# Validate response structure
if "results" not in results:
    print(f"Unexpected API response structure: {results}")
    exit(1)

# Write results to CSV (order: Project, Repository, File, Path)
csv_filename = "ado_search_results.csv"
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Project", "Repository", "File", "Path"])  # Column headers in correct order

    for item in results.get("results", []):
        if not isinstance(item, dict):
            print(f"⚠️ Unexpected item format: {item}")
            continue

        project_name = item.get("project", {}).get("name", "Unknown Project")
        repo_name = item.get("repository", {}).get("name", "Unknown Repo")
        file_name = item.get("fileName", "Unknown File")
        file_path = item.get("path", "Unknown Path")

        writer.writerow([project_name, repo_name, file_name, file_path])  # Correct column order

print(f"✅ Search results saved in {csv_filename}")