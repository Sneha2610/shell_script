import os
import requests
import pandas as pd
import csv

# Constants
IP_FILE = 'ips.txt'  # List of IPs
CSV_FILE = 'repos.csv'  # CSV with Project Name and Repository Name
REPORT_FILE = 'ip_search_report.csv'  # Output CSV report
ADO_ORG = 'your_organization'  # Replace with your Azure DevOps organization
API_VERSION = '7.1-preview.1'
TOKEN = os.getenv('TOKEN')  # Get PAT from environment variable

# Prepare authorization header
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {os.getenv("TOKEN")}':
}

# Read IPs from file
def load_ips(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Function to search IPs using ADO Search API
def search_ip_in_repo(project, repo, search_text):
    url = f'https://dev.azure.com/{ADO_ORG}/{project}/_apis/search/codesearchresults?api-version={API_VERSION}'
    payload = {
        "searchText": search_text,
        "filters": {
            "Repository": repo
        }
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error searching in {project}/{repo}: {response.status_code} - {response.text}")
        return None

# Parse search results
def parse_results(results, project, repo):
    matches = []
    for result in results.get('results', []):
        for match in result.get('matches', []):
            matches.append({
                'Project': project,
                'Repository': repo,
                'File': match.get('filePath', 'N/A'),
                'Line Number': match.get('lineNumber', 'N/A')
            })
    return matches

# Main function
def main():
    ips = load_ips(IP_FILE)
    df = pd.read_csv(CSV_FILE)
    results = []

    for _, row in df.iterrows():
        project = row['Project Name']
        repo = row['Repository Name']
        print(f"Searching in {project}/{repo}...")
        for ip in ips:
            search_results = search_ip_in_repo(project, repo, ip)
            if search_results:
                matches = parse_results(search_results, project, repo)
                results.extend(matches)

    # Save to CSV
    if results:
        keys = results[0].keys()
        with open(REPORT_FILE, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f'Report generated: {REPORT_FILE}')
    else:
        print("No IP matches found.")

if __name__ == '__main__':
    main()
