import requests
import csv

# Replace these variables with your values
ado_org = "your_ado_organization"  # e.g., 'myorg'
project_name = "security"  # The project you're interested in
pat = "your_personal_access_token"  # Your Azure DevOps PAT

# Azure DevOps API URL for fetching repositories
url = f"https://dev.azure.com/{ado_org}/{project_name}/_apis/git/repositories?api-version=6.0"

# Create the authentication headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {requests.auth._basic_auth_str("", pat)}'
}

# Send the request to get repository information
response = requests.get(url, headers=headers)
if response.status_code == 200:
    repos = response.json()['value']
else:
    print(f"Failed to fetch repositories: {response.status_code}")
    exit()

# File path to save the CSV
csv_file_path = 'ado_repositories.csv'

# Writing the repositories to a CSV file
with open(csv_file_path, mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['Project Name', 'Repository Name'])  # Write header

    for repo in repos:
        csv_writer.writerow([project_name, repo['name']])

print(f"Repository list saved to {csv_file_path}")
