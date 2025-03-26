import os
import requests
import base64
import csv

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

# Check response
if response.status_code == 200:
    results = response.json()

    # Write results to CSV
    csv_filename = "ado_search_results.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Repository", "File Path", "Matched Content"])

        for item in results.get("results", []):
            repo_name = item.get("repository", {}).get("name", "Unknown Repo")
            file_path = item.get("path", "Unknown Path")
            match_content = item.get("matches", [])
            matched_text = "\n".join(m.get("fragment", "") for m in match_content)

            writer.writerow([repo_name, file_path, matched_text])

    print(f"Search results saved in {csv_filename}")

else:
    print(f"Error {response.status_code}: {response.text}")