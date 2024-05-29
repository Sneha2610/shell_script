import requests
import base64

# Azure DevOps organization URL and project details
organization = 'your_organization'
project = 'your_project'
repository_id = 'your_repository_id'

# Personal Access Token (PAT)
personal_access_token = 'your_pat'

# Base64 encode the PAT for Basic Auth
auth_header = base64.b64encode(f':{personal_access_token}'.encode()).decode()

# API URL to list branches
list_branches_url = f'https://dev.azure.com/{organization}/{project}/_apis/git/repositories/{repository_id}/refs?filter=refs/heads/&api-version=6.0'

# Make the request to list branches
response = requests.get(
    list_branches_url,
    headers={
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/json'
    }
)

# Check the response
if response.status_code == 200:
    branches = response.json()['value']
    print(f"Found {len(branches)} branches:")
    for branch in branches:
        branch_name = branch['name']
        print(f"- {branch_name}")
else:
    print(f'Failed to list branches')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
