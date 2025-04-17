import csv
import requests
import re
import os
import json

# ------------------ Config ------------------
ADO_ORG = "your-org-name"  # 🔁 Replace with your Azure DevOps org name
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")  # 🔐 Ensure this is set: export ADO_PAT=yourPAT

# Regex to match IPv4 addresses
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Basic Auth
auth = requests.auth.HTTPBasicAuth('', PAT)
headers = {
    "Content-Type": "application/json"
}

# Load repos from CSV
with open('repo.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    repo_list = [row for row in reader]

# Write results to output.csv
with open('output.csv', mode='w', newline='', encoding='utf-8') as out_file:
    fieldnames = ['Project', 'Repository', 'File', 'IP Found']
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in repo_list:
        project = entry['project']
        repo = entry['repository']
        print(f"\n🔍 Scanning: {project}/{repo}")

        # API URL
        url = f"https://almsearch.dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults?api-version={API_VERSION}"

        # Payload for the POST request
        payload = {
            "searchText": ".",
            "filters": {
                "Repository": [repo]
            },
            "$top": 100
        }

        try:
            resp = requests.post(url, headers=headers, auth=auth, json=payload)

            # Debug HTTP response
            print(f"🔎 HTTP Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"❌ Error for {repo}:\n{resp.text[:300]}")
                continue

            try:
                data = resp.json()
            except json.JSONDecodeError:
                print("❌ Couldn't decode JSON. Raw text:")
                print(resp.text[:300])
                continue

            if not isinstance(data, dict):
                print("❌ Unexpected response type (not a dict):")
                print(data)
                continue

            results = data.get('results', [])
            if not isinstance(results, list):
                print("⚠️ 'results' is not a list. Skipping.")
                continue

            for result in results:
                file_path = result.get('path', '')
                matches = result.get('matches', [])
                for match in matches:
                    line = match.get('line', '')
                    line_clean = line.encode('utf-8', errors='replace').decode('utf-8')
                    ips = ip_regex.findall(line_clean)
                    for ip in ips:
                        writer.writerow({
                            'Project': project,
                            'Repository': repo,
                            'File': file_path,
                            'IP Found': ip
                        })
                        print(f"[+] {ip} in {repo}/{file_path}")

        except Exception as e:
            print(f"❌ Exception for {project}/{repo}: {e}")
