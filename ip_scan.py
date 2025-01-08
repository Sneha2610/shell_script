import os
import subprocess
import requests

def get_repositories(organization, project, pat):
    """
    Fetch all repositories in a specific Azure DevOps project.

    Args:
        organization (str): Azure DevOps organization URL (e.g., https://dev.azure.com/orgname).
        project (str): Name of the project to scan.
        pat (str): Personal Access Token for authentication.

    Returns:
        list: List of repository names.
    """
    url = f"{organization}/{project}/_apis/git/repositories?api-version=7.1-preview.1"
    response = requests.get(url, auth=("", pat))
    if response.status_code != 200:
        raise Exception(f"Failed to fetch repositories: {response.text}")
    repos = response.json().get("value", [])
    return [repo["name"] for repo in repos]

def clone_and_scan_repo(repo_url, repo_name, gitleaks_binary, rules_file, output_dir):
    """
    Clone a repository and run Gitleaks scan.

    Args:
        repo_url (str): Git URL of the repository.
        repo_name (str): Name of the repository.
        gitleaks_binary (str): Path to the Gitleaks binary.
        rules_file (str): Path to the Gitleaks rules file.
        output_dir (str): Directory to save Gitleaks reports.
    """
    repo_dir = os.path.join(output_dir, repo_name)
    os.makedirs(repo_dir, exist_ok=True)

    try:
        # Clone the repository
        print(f"Cloning repository: {repo_name}")
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_name}: {e}")
        return  # Skip this repository and continue with the next one

    try:
        # Run Gitleaks
        report_file = os.path.join(output_dir, f"{repo_name}_report.json")
        print(f"Running Gitleaks scan on {repo_name}")
        subprocess.run(
            [
                gitleaks_binary,
                "detect",
                "--source",
                repo_dir,
                "--config",
                rules_file,
                "--report-format",
                "json",
                "--report-path",
                report_file,
            ],
            check=True,
        )
        print(f"Report saved: {report_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error running Gitleaks on {repo_name}: {e}")

def main():
    # Configuration
    organization = "https://dev.azure.com/your-org-name"  # Replace with your organization
    project = "your-project-name"  # Replace with your project name
    pat = os.getenv("ADO_PAT")  # Access the PAT from environment variable
    gitleaks_binary = "./gitleaks"  # Path to your Gitleaks binary
    rules_file = "./rules.toml"  # Path to your Gitleaks rules file
    output_dir = "./gitleaks_reports"  # Directory to save reports

    if not pat:
        raise EnvironmentError("ADO_PAT environment variable is not set. Ensure your pipeline is configured correctly.")

    os.makedirs(output_dir, exist_ok=True)

    try:
        # Fetch all repositories in the project
        print(f"Fetching repositories in project: {project}")
        repos = get_repositories(organization, project, pat)

        # Clone and scan each repository
        for repo_name in repos:
            repo_url = f"https://{pat}@dev.azure.com/{organization.split('/')[-1]}/{project}/_git/{repo_name}"
            clone_and_scan_repo(repo_url, repo_name, gitleaks_binary, rules_file, output_dir)

        print("Gitleaks scan completed for all repositories.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
