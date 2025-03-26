import os
import requests
import base64
import csv
import json
import time

# Azure DevOps Organization Name
ORG_NAME = "your-organization"

# Read PAT from Environment Variable
PAT = os.getenv("TOKEN")
if not PAT:
    raise ValueError("PAT is not set. Ensure 'TOKEN' is declared in the ADO pipeline environment.")

# API URL (Org-wide search)
API_URL = f"https://almsearch.dev.azure.com/{ORG_NAME}/_apis/search/codesearchresults?api-version=7.1-preview.1"

# Authentication (Base64 encode the PAT)
auth_header = base64.b64encode(f":{PAT}".encode()).decode()

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_header}"
}

# Input file containing 2000+ search terms (one per line)
SEARCH_FILE = "search_terms.txt"

# Output CSV file
CSV_FILENAME = "ado_bulk_search_results.csv"

# Read search terms from file
with open(SEARCH_FILE, "r", encoding="utf-8") as file:
    search_terms = [line.strip() for line in file if line.strip()]

# Write results to CSV
with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Search Term", "Project", "Repository", "File", "Path"])  # Column headers

    for term in search_terms:
        print(f"🔍 Searching for: {term}")

        payload = {
            "searchText": term,
            "$top": 100  # Adjust if needed
        }

        # Make API request
        response = requests.post(API_URL, json=payload, headers=headers)

        # Handle potential API rate limits
        if response.status_code == 429:
            print("⚠️ Rate limit hit. Sleeping for 60 seconds...")
            time.sleep(60)
            continue

        # Parse JSON response
        try:
            results = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"❌ Error decoding JSON for {term}: {response.text}")
            continue

        # Validate response structure
        if "results" not in results:
            print(f"⚠️ No results found for {term}")
            continue

        # Extract and write results
        for item in results.get("results", []):
            project_name = item.get("project", {}).get("name", "Unknown Project")
            repo_name = item.get("repository", {}).get("name", "Unknown Repo")
            file_name = item.get("fileName", "Unknown File")
            file_path = item.get("path", "Unknown Path")

            writer.writerow([term, project_name, repo_name, file_name, file_path])

print(f"✅ All search results saved in {CSV_FILENAME}")