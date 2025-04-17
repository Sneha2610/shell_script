import csv
import requests
import re
import os
import base64

# --- Configuration ---
ADO_ORG = "your-org-name"  # 🔁 Replace this with your actual Azure DevOps organization name
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")

if not PAT:
    raise ValueError("❌ ADO_PAT environment variable not set")

# Encode PAT for basic auth
encoded_pat = base64.b64encode(f":{PAT}".encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded_pat}"
}

# IPv4 regex
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# --- Load repositories from repo.csv ---
with open('repo.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    repos = [row for row in reader]

# --- Write to output.csv ---
with open('output.csv', mode='w', newline='', encoding='utf-8', errors='replace') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=['Project', 'Repository', 'File', 'IP Found'])
    writer.writeheader()

    for repo_entry in repos:
        project = repo_entry['project']
        repo = repo_entry['repository']
        print(f"🔍 Searching {project}/{repo}")

        # Prepare search API payload
        search_url = f"https://almsearch.dev.azure.com/{ADO_ORG}/_apis/search/codesearchresults?api-version={API_VERSION}"
        payload = {
            "searchText": ".",
            "filters": {
                "Project": [project],
                "Repository": [repo]
            },
            "$top": 1000
        }

        try:
