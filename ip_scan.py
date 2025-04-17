import csv
import requests
import re
import os
import base64

# Config
ADO_ORG = "your-org-name"  # Replace with your Azure DevOps organization name
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")

if not PAT:
    raise EnvironmentError("Environment variable ADO_PAT not set.")

# Auth header
encoded_pat = base64.b64encode(f":{PAT}".encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {encoded_pat}"
}

# IPv4 Regex
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Load repo list
with open('repo.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    repos = [row for row in reader]

# Write output
with open('output.csv', mode='w', newline='', encoding='utf-8', errors='replace') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=['Project', 'Repository', 'File', 'IP Found'])
    writer.writeheader()

    for repo_entry in repos:
        project = repo_entry['project']
        repository = repo_entry['repository']
        print(f"🔍 Scanning {project}/{repository}")

        search_url = f"https://dev.azure.com/{ADO_ORG}/_apis/search/codesearchresults?api-version={API_VERSION}"

        payload = {
            "searchText": ".",
            "filters": {
                "Project": [project],
                "Repository": [repository]
            },
            "$top": 1000
        }

        response = requests.post(search_url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Failed for {project}/{repository}: {response.status_code}")
            print(response.text[:300])  # Print first part of HTML to help debug
            continue

        for result in response.json().get('results', []):
            file_path = result.get('path', '')
            for match in result.get('matches', []):
                line = match.get('line', '')
                line = line.encode('utf-8', errors='replace').decode('utf-8')
                for ip in ip_regex.findall(line):
                    writer.writerow({
                        'Project': project,
                        'Repository': repository,
                        'File': file_path,
                        'IP Found': ip
                    })
                    print(f"✅ Found IP: {ip} in {file_path}")
