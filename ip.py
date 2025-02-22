import os
import requests
import pandas as pd

# Get token from environment variable
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable not set!")

# Azure DevOps configurations
ADO_ORG = "your_organization"  # Replace with your Azure DevOps organization
API_VERSION = "7.1-preview.1"
BASE_URL = f"https://dev.azure.com/{ADO_ORG}"

# Prepare authorization headers without base64 encoding
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic :{TOKEN}'  # Directly using the PAT
}

# Load IP list from a file
ip_file = "ips.txt"  # Replace with your actual file path
with open(ip_file, 'r') as file:
    ip_list = [line.strip() for line in file.readlines() if line.strip()]

# Function to search for an IP in a repo using Azure DevOps Code Search API
def search_ip_in_repo(project, repo, ip):
    url = f"{BASE_URL}/{project}/_apis/search/codesearchresults?api-version={API_VERSION}"
    payload = {
        "searchText": ip,
        "filters": {
            "Repository": [repo]
        }
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error searching in {project}/{repo}: {response.status_code}")
        print("Response Text:", response.text)  # Debugging HTML responses
        return None

# Load list of projects and repositories from CSV
repo_csv = "repos.csv"  # Replace with your actual CSV file path
df_repos = pd.read_csv(repo_csv)

# Prepare results list
results = []

# Iterate through all IPs and repositories
for _, row in df_repos.iterrows():
    project = row['Project Name']
    repo = row['Repository Name']

    for ip in ip_list:
        search_results = search_ip_in_repo(project, repo, ip)
        if search_results and "results" in search_results:
            for result in search_results["results"]:
                file_path = result.get("path", "Unknown")
                for match in result.get("matches", []):
                    line_number = match.get("line", "Unknown")
                    results.append({
                        "Project": project,
                        "Repository": repo,
                        "File": file_path,
                        "Line Number": line_number,
                        "IP Found": ip
                    })

# Convert results to DataFrame and export as CSV
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv("ip_search_report.csv", index=False)
    print("Report generated: ip_search_report.csv")
else:
    print("No IPs found in any repositories.")