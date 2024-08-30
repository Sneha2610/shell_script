import os
import requests

# Fetch PAT from environment variables
pat = os.getenv('AZURE_DEVOPS_PAT')
if not pat:
    raise ValueError("The PAT is not set as an environment variable.")

organization = "your_organization"

# API URL to fetch all projects
projects_url = f"https://dev.azure.com/{organization}/_apis/projects?api-version=7.1-preview.4"

# Headers for authentication
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {pat}'
}

# Fetch all projects
response = requests.get(projects_url, headers=headers)
if response.status_code == 200:
    projects = response.json()['value']
else:
    print(f"Failed to fetch projects: {response.status_code}")
    exit()

# Open a text file to write the repository names
with open('all_repositories.txt', 'w') as file:
    # Iterate over all projects
    for project in projects:
        project_name = project['name']
        print(f"Fetching repos for project: {project_name}")
        
        # API URL to fetch repositories in the current project
        repos_url = f"https://dev.azure.com/{organization}/{project_name}/_apis/git/repositories?api-version=7.1-preview.1"
        
        # Fetch repositories for the project
        repos_response = requests.get(repos_url, headers=headers)
        if repos_response.status_code == 200:
            repos = repos_response.json()['value']
            # Write repository names to the text file
            for repo in repos:
                repo_name = repo['name']
                file.write(f"{project_name}: {repo_name}\n")
        else:
            print(f"Failed to fetch repos for project {project_name}: {repos_response.status_code}")

print("Repository names have been saved to 'all_repositories.txt'")
