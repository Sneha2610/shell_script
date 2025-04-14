import os
import csv
import base64
import re
import requests
import urllib.parse

# === CONFIG ===
ADO_ORG_URL = "https://dev.azure.com/YOUR_ORG_NAME"  # Replace this!
PAT = os.getenv("ADO_PAT")
INPUT_CSV = "input.csv"
OUTPUT_CSV = "output_ips.csv"

if not PAT:
    raise EnvironmentError("ADO_PAT environment variable not set")

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f':{PAT}'.encode()).decode()
}

ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

def get_repo_id(project, repo_name):
    encoded_project = urllib.parse.quote(project.strip(), safe='')
    encoded_repo = urllib.parse.quote(repo_name.strip(), safe='')
    url = f"{ADO_ORG_URL}/{encoded_project}/_apis/git/repositories/{encoded_repo}?api-version=7.1-preview.1"
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        print(f"❌ Failed to fetch repo ID for '{repo_name}' in project '{project}'")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        response.raise_for_status()
    return response.json()['id']

def get_items(project, repo_id):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items"
    params = {
        "recursionLevel": "Full",
        "api-version": "7.1-preview.1"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get('value', [])

def get_file_content(project, repo_id, path):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items"
    params = {
        "path": path,
        "api-version": "7.1-preview.1",
        "includeContent": "true"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()

        if not response.content:
            print(f"🚫 No content returned for: {path}")
            return ""

        try:
            json_data = response.json()
        except ValueError:
            if "<html" in response.text.lower():
                print(f"⚠️ Received HTML instead of JSON for {path} (possible error page)")
            else:
                print(f"⚠️ Invalid JSON for {path}. Raw response: {response.text[:300]}")
            return ""

        if 'content' not in json_data:
            print(f"⚠️ 'content' field missing in JSON for: {path}")
            return ""

        return json_data['content']

    except requests.exceptions.HTTPError as e:
        if response.status_code == 400 and "too large" in response.text.lower():
            print(f"⚠️ Skipping large file: {path}")
        elif response.status_code == 403:
            print(f"🚫 Permission denied for: {path}")
        elif response.status_code == 404:
            print(f"🚫 File not found: {path}")
        else:
            print(f"❌ HTTP Error {response.status_code} for {path}: {response.text[:300]}")
        return ""
    except Exception as e:
        print(f"⚠️ Unexpected error on {path}: {e}")
        return ""

def main():
    results = []

    with open(INPUT_CSV, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            project = row['project'].strip()
            repo_name = row['repo'].strip()
            print(f"\n🔍 Scanning repo '{repo_name}' in project '{project}'")

            try:
                repo_id = get_repo_id(project, repo_name)
                items = get_items(project, repo_id)

                for item in items:
                    if item.get('isFolder', False):
                        continue

                    file_path = item['path']
                    if not file_path.endswith(('.yml', '.yaml', '.json', '.py', '.sh', '.conf', '.txt', '.cs', '.js', '.xml')):
                        continue

                    try:
                        content = get_file_content(project, repo_id, file_path)
                        ips = ip_regex.findall(content)
                        for ip in ips:
                            results.append({
                                'project': project,
                                'repo': repo_name,
                                'file': file_path,
                                'ip': ip
                            })
                    except Exception as e:
                        print(f"⚠️ Error reading file {file_path}: {e}")

            except Exception as e:
                print(f"❌ Error with repo '{repo_name}' in project '{project}': {e}")

    # Write output
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        fieldnames = ['project', 'repo', 'file', 'ip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Scan complete. IPs saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
