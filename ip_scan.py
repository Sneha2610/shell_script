import csv
import requests
import re
import os
import json

# ------------------ Config ------------------
ADO_ORG = "your-org-name"  # 🔁 Replace with your Azure DevOps org name
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")  # 🔐 Set your PAT as an environment variable

# Regex for IPv4
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Auth and headers
auth = requests.auth.HTTPBasicAuth('', PAT)
headers = {"Content-Type": "application/json"}

# ------------------ Load Repos ------------------
with open('repo.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    repo_list = [row for row in reader]

# ------------------ Output CSV ------------------
with open('output.csv', mode='w', newline='', encoding='utf-8', errors='replace') as out_file:
    fieldnames = ['Project', 'Repository', 'File', 'IP Found']
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    writer.writeheader()

    for entry in repo_list:
        project = entry['project']
        repo = entry['repository']
        print(f"🔍 Scanning: {project}/{repo}")

        # Search URL and payload
        url = f"https://almsearch.dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults?api-version={API_VERSION}"
        payload = {
            "searchText": ".",
            "filters": {
                "Project": [project],
                "Repository": [repo]
            },
            "$top": 100
        }

        try:
            resp = requests.post(url, headers=headers, auth=auth, json=payload)
            if resp.status_code != 200:
                print(f"❌ {project}/{repo} failed: {resp.status_code} - {resp.text}")
                continue

            data = resp.json()

            # Optional: save raw response for debugging
            with open(f"debug_{project}_{repo}.json", "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            results = data.get('results', [])

            if isinstance(results, str):
                print(f"⚠️ Skipped {repo}: Unexpected string in 'results'")
                continue

            for result in results:
                if not isinstance(result, dict):
                    continue
                file_path = result.get('path', '')
                matches = result.get('matches', [])
                for match in matches:
                    line = match.get('line', '')
                    line = line.encode('utf-8', errors='replace').decode('utf-8')
                    ips = ip_regex.findall(line)
                    for ip in ips:
                        writer.writerow({
                            'Project': project,
                            'Repository': repo,
                            'File': file_path,
                            'IP Found': ip
                        })
                        print(f"[+] {ip} found in {repo}{file_path}")

        except Exception as e:
            print(f"🔥 Error processing {repo}: {e}")
