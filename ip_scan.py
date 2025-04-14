import os
import csv
import base64
import re
import requests
import urllib.parse

# === CONFIG ===
ADO_ORG_URL = "https://dev.azure.com/YOUR_ORG_NAME"  # <-- Replace this with your ADO org name
PAT = os.getenv("ADO_PAT")
INPUT_CSV = "input.csv"
OUTPUT_CSV = "output_ips.csv"

if not PAT:
    raise EnvironmentError("ADO_PAT environment variable not set")

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f":{PAT}".encode()).decode()
}

ip_regex = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

def get_repo_id(project, repo_name):
    encoded_project = urllib.parse.quote(project.strip(), safe='')
    encoded_repo = urllib.parse.quote(repo_name.strip(), safe='')
    url = f"{ADO_ORG_URL}/{encoded_project}/_apis/git/repositories/{encoded_repo}?api-version=7.1-preview.1"
    response = requests.get(url, headers=HEADERS)
    if not response.ok:
        print(f"\n❌ Failed to fetch repo ID for '{repo_name}' in project '{project}'")
        print(f"🔗 URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
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
        response.raise_for_status()  # Will raise an exception for 4xx/5xx status codes
        if not response.content:  # If content is empty
            print(f"🚫 No content returned for file: {path}")
            return ""

        # Try to parse the response as JSON
        try:
            json_data = response.json()
        except ValueError:
            print(f"⚠️ Invalid JSON for {path}: {response.text}")
            return ""

        # Check if 'content' is in the response JSON
        if 'content' not in json_data:
            print(f"🚫 Skipping (no content field) for file: {path}")
            return ""

        return json_data['content']

    except requests.exceptions.HTTPError as e:
        if response.status_code == 400 and "too large" in response.text.lower():
            print(f"🚫 Skipping large file: {path}")
        else:
            print(f"❌ HTTP Error on {path}: {response.status_code} - {response.text}")
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

    # Write output CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        fieldnames = ['project', 'repo', 'file', 'ip']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Scan complete! Results written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
