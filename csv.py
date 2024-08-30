import os
import requests
import base64
import csv

# Fetch PAT from environment variables
pat = os.getenv('AZURE_DEVOPS_PAT')
if not pat:
    raise ValueError("The PAT is not set as an environment variable.")

organization = "your_organization"

# Base64 encode the PAT for basic authentication
pat_base64 = base64.b64encode(f":{pat}".encode()).decode()

# API URL to fetch all projects
projects_url = f"https://dev.azure.com/{organization}/_apis/projects?api-version=7.1-preview.4"

# Headers for authentication
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {pat_base64}'
}

# Fetch all projects
response = requests.get(projects_url, headers=headers)

# Debugging: Print the status code and content if the request fails
if response.status_code != 200:
    print(f"Failed to fetch projects: {response.status_code}")
    print(f"Response content: {response.content.decode()}")
    exit()

projects = response.json()['value']

# Open a CSV file to write the project and repository names
with open('projects_and_repositories.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write header row
    csvwriter.writerow(['Project Name', 'Repository Name'])

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
            # Write project and repository names to the CSV file
            for repo in repos:
                repo_name = repo['name']
                csvwriter.writerow([project_name, repo_name])
        else:
            print(f"Failed to fetch repos for project {project_name}: {repos_response.status_code}")
            print(f"Response content: {repos_response.content.decode()}")

print("Project and repository names have been saved to 'projects_and_repositories.csv'")
