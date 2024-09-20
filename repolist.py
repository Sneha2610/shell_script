import requests
import csv
import base64
import os

# Replace these variables with your values
ado_org = "your_ado_organization"  # e.g., 'myorg'
project_name = "security"  # The project you're interested in
pat = os.getenv("ADO_PAT")  # Fetching the token from environment variable ADO_PAT

if not pat:
    print("Personal Access Token (PAT) not found in environment variables. Please set ADO_PAT.")
    exit()

# Azure DevOps API URL for fetching repositories
url = f"https://dev.azure.com/{ado_org}/{project_name}/_apis/git/repositories?api-version=7.0"

# Create the authentication headers
pat_bytes = f":{pat}".encode('ascii')
pat_base64 = base64.b64encode(pat_bytes).decode('ascii')
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {pat_base64}'
}

# Send the request to get repository information
response = requests.get(url, headers=headers)

# Debugging: Print the raw response
print(f"Status Code: {response.status_code}")
print(f"Response Content: {response.text}")

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
