import csv
import requests
import re
import os

# ------------------ Config ------------------
ADO_ORG = "your-org-name"  # 🔁 Replace with your Azure DevOps org name
API_VERSION = "7.1-preview.1"
PAT = os.environ.get("ADO_PAT")  # 🔐 Set your PAT as an environment variable

# Regex for IPv4
ip_regex = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b')

# Auth and headers
auth = requests.auth.HTTPBasicAuth('', PAT)
headers = {"Content-Type": "application/json"}

# ------------------ Load repo.csv ------------------
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
        print(f"\n🔍 Scanning: {project}/{repo}")

        # Build URL
        url = f"https://almsearch.dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults?api-version={API_VERSION}"

        # Payload to search everything (you can change searchText to specific IP if needed)
        payload = {
            "searchText": ".",  # Search all code
            "filters": {
                "Repository": [repo]
            },
            "$top": 100
        }

        try:
            response = requests.post(url, headers=headers, auth=auth, json=payload)

            print(f"🔎 Status Code: {response.status_code}")
            print(f"🔎 Content-Type: {response.headers.get('Content-Type')}")
            if response.status_code != 200:
                print(f"❌ Request failed for {repo}: {response.text[:200]}")
                continue

            try:
                data = response.json()
            except ValueError:
                print("❌ Failed to parse JSON response. Raw content:")
                print(response.text[:300])
                continue

            results = data.get('results', [])
            for result in results:
                file_path = result.get('path', '')
                matches = result.get('matches', [])
                for match in matches:
                    line = match.get('line', '')
                    clean_line = line.encode('utf-8', errors='replace').decode('utf-8')
                    ips = ip_regex.findall(clean_line)
                    for ip in ips:
                        writer.writerow({
                            'Project': project,
                            'Repository': repo,
                            'File': file_path,
                            'IP Found': ip
                        })
                        print(f"[+] {ip} found in {repo}{file_path}")

        except Exception as e:
            print(f"❌ Exception for {project}/{repo}: {e}")
