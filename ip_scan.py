import csv
import requests
import re
import os

# ------------------ Config ------------------
ADO_ORG = "your-org-name"  # 🔁 Replace with your Azure DevOps org
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")  # 🔐 Set your PAT as an environment variable

# Regex for IPv4
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Auth setup
auth = requests.auth.HTTPBasicAuth('', PAT)
headers = { "Content-Type": "application/json" }

# ------------------ Load Repos from repo.csv ------------------
with open('repo.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    repo_list = [row for row in reader]

# ------------------ Output to output.csv ------------------
with open('output.csv', mode='w', newline='', encoding='utf-8', errors='replace') as out_file:
    fieldnames = ['Project', 'Repository', 'File', 'IP Found']
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in repo_list:
        project = entry['project']
        repo = entry['repository']
        print(f"🔍 Scanning: {project}/{repo}")

        # Build search URL
        search_url = (
            f"https://almsearch.dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults"
            f"?api-version={API_VERSION}"
            f"&$top=1000"
            f"&searchText=."
            f"&filters=Repository:{repo}"
        )

        # Send request
        resp = requests.get(search_url, auth=auth, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Failed for {repo}: {resp.status_code} - {resp.text}")
            continue

        results = resp.json().get('results', [])
        for result in results:
            file_path = result.get('path', '')
            matches = result.get('matches', [])
            for match in matches:
                line = match.get('line', '')
                line = line.encode('utf-8', errors='replace').decode('utf-8')  # 🧼 Clean line
                ips = ip_regex.findall(line)
                for ip in ips:
                    writer.writerow({
                        'Project': project,
                        'Repository': repo,
                        'File': file_path,
                        'IP Found': ip
                    })
                    print(f"[+] {ip} found in {repo}{file_path}")
