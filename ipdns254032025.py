import requests
import base64
import csv
import os

# Azure DevOps Configuration
ADO_ORG = "your-org-name"
ADO_PAT = os.getenv("ADO_PAT")  # Read PAT from environment variable

if not ADO_PAT:
    raise ValueError("Personal Access Token (ADO_PAT) is not set in environment variables.")

# Headers for authentication
HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f":{ADO_PAT}".encode()).decode(),
    "Content-Type": "application/json"
}

# Read search terms from file
def load_search_terms(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Get all projects
def get_projects():
    url = f"https://dev.azure.com/{ADO_ORG}/_apis/projects?api-version=7.0"
    response = requests.get(url, headers=HEADERS).json()
    return [project["name"] for project in response.get("value", [])]

# Get repositories for a project
def get_repositories(project):
    url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/git/repositories?api-version=7.0"
    response = requests.get(url, headers=HEADERS).json()
    return [repo["name"] for repo in response.get("value", [])]

# Search in repositories (file paths & contents)
def search_in_repositories(term, project):
    results = []
    repos = get_repositories(project)

    for repo in repos:
        url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/git/repositories/{repo}/items?recursionLevel=full&api-version=7.0"
        response = requests.get(url, headers=HEADERS).json()
        for item in response.get("value", []):
            if "path" in item and term in item["path"]:
                results.append(f"{project}/{repo} -> {item['path']}")

    return results

# Search in pipelines logs
def search_in_pipelines(term, project):
    url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/build/builds?api-version=7.0"
    builds = requests.get(url, headers=HEADERS).json()
    
    results = []
    for build in builds.get("value", []):
        build_id = str(build["id"])  # Ensure ID is string
        log_url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/build/builds/{build_id}/logs?api-version=7.0"
        logs = requests.get(log_url, headers=HEADERS).json()
        
        for log in logs.get("value", []):
            log_id = str(log["id"])  # Ensure ID is string
            log_content_url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/build/builds/{build_id}/logs/{log_id}?api-version=7.0"
            log_content = requests.get(log_content_url, headers=HEADERS).text
            if term in log_content:
                results.append(f"{project} -> Pipeline log #{build_id}")

    return results

# Search in work items (Titles & Descriptions)
def search_in_work_items(term, project):
    url = f"https://dev.azure.com/{ADO_ORG}/{project}/_apis/wit/wiql?api-version=7.0"
    query = {"query": f"SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.Title] CONTAINS '{term}' OR [System.Description] CONTAINS '{term}'"}
    response = requests.post(url, json=query, headers=HEADERS).json()
    
    results = []
    for work_item in response.get("workItems", []):
        work_item_id = str(work_item['id'])  # Ensure ID is string
        results.append(f"{project} -> Work Item #{work_item_id}")
    
    return results

# Scan all projects, write results row-by-row
def scan_and_write_results(input_file, output_file):
    search_terms = load_search_terms(input_file)
    projects = get_projects()

    with open(output_file, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["IP/DNS", "Found In"])

        for term in search_terms:
            found_locations = []

            for project in projects:
                found_locations.extend(search_in_repositories(term, project))
                found_locations.extend(search_in_pipelines(term, project))
                found_locations.extend(search_in_work_items(term, project))

            if found_locations:
                csv_writer.writerow([term, "; ".join(found_locations)])
            else:
                csv_writer.writerow([term, "Not Found"])

# Run the scan
input_file = "ips_dns.txt"  # File containing list of IPs/DNS
output_file = "search_results.csv"

scan_and_write_results(input_file, output_file)
print(f"Scan completed! Results saved in {output_file}")