import csv
import requests
import re
import os

# ------------------ Config ------------------
ADO_ORG = "your-org-name"  # Change this
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")  # Export PAT as an env variable

# Regex for IPv4
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Headers and auth
auth = requests.auth.HTTPBasicAuth('', PAT)
headers = { "Content-Type": "application/json" }

# ------------------ Load Repos ------------------
with open('repo.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    repo_list = [row for row in reader]

# ------------------ Output CSV ------------------
with open('output.csv', mode='w', newline='') as out_file:
    fieldnames = ['Project', 'Repository', 'File', 'IP Found']
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in repo_list:
        project = entry['project']
        repo = entry['repository']
        print(f"🔍 Scanning: {project}/{repo}")

        search_url = (
            f"https://almsearch.dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults"
            f"?api-version={API_VERSION}"
            f"&$top=1000"
            f"&searchText=."
            f"&filters=Repository:{repo}"
        )

        resp = requests.get(search_url, auth=auth, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Failed for {repo}: {resp.status_code}")
            continue

        results = resp.json().get('results', [])
        for result in results:
            file_path = result.get('path', '')
            matches = result.get('matches', [])
            for match in matches:
                line = match.get('line', '')
                ips = ip_regex.findall(line)
                for ip in ips:
                    writer.writerow({
                        'Project': project,
                        'Repository': repo,
                        'File': file_path,
                        'IP Found': ip
                    })
                    print(f"[+] {ip} found in {repo}{file_path}")
