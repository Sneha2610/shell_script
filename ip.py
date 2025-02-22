import os
import base64
import requests
import pandas as pd

# Get token from environment variable
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN environment variable not set!")

# Encode token for Basic Authentication
basic_token = base64.b64encode(f":{TOKEN}".encode()).decode()

# Azure DevOps configurations
ADO_ORG = "your_organization"  # Replace with your Azure DevOps organization
API_VERSION = "7.1"
BASE_URL = f"https://almsearch.dev.azure.com/{ADO_ORG}/_apis/search/codesearchresults?api-version={API_VERSION}"

# Prepare authorization headers using Basic Auth
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {basic_token}'
}

# Load IP list from a file
ip_file = "ips.txt"
with open(ip_file, 'r') as file:
    ip_list = [line.strip() for line in file if line.strip()]

# Function to search for an IP across the organization using POST
def search_ip(ip):
    payload = {
        "searchText": ip
    }
    
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error searching for IP {ip}: {response.status_code}")
        print("Response Text:", response.text[:500])  # Debug first 500 chars of response
        return None

# Collect results
results = []

# Iterate through all IPs and search across the organization
for ip in ip_list:
    search_results = search_ip(ip)
    if search_results and "results" in search_results:
        for result in search_results["results"]:
            project_name = result.get("project", {}).get("name", "Unknown")
            repo_name = result.get("repository", {}).get("name", "Unknown")
            file_path = result.get("path", "Unknown")
            for match in result.get("matches", []):
                line_number = match.get("line", "Unknown")
                results.append({
                    "IP Found": ip,
                    "Project": project_name,
                    "Repository": repo_name,
                    "File Path": file_path,
                    "Line Number": line_number
                })

# Export results to CSV
if results:
    results_df = pd.DataFrame(results)
    results_df.to_csv("org_ip_search_report.csv", index=False)
    print("Report generated: org_ip_search_report.csv")
else:
    print("No IPs found across the organization.")