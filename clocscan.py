import os
import subprocess
import requests

# Hardcoded Azure DevOps configuration
ADO_ORG_URL = "https://dev.azure.com/yourorganization/"  # Replace with your actual organization URL
ADO_TOKEN = os.environ.get("TOKEN")  # Personal Access Token (set in the pipeline)
PROJECTS_FILE = "projects.txt"         # File with one project name per line
AUTH = ('', ADO_TOKEN)

def list_repositories(project):
    """Lists all repositories in the given project using the Azure DevOps REST API."""
    url = f"{ADO_ORG_URL}{project}/_apis/git/repositories?api-version=6.0"
    response = requests.get(url, auth=AUTH)
    if response.status_code == 200:
        repos = response.json().get("value", [])
        print(f"Found {len(repos)} repositories in project {project}.")
        return repos
    else:
        print(f"Failed to list repositories for project {project}: {response.status_code} - {response.text}")
        return []

def clone_repository(project, repo_name):
    """
    Clones the specified repository.
    Note: Replace 'yourorganization' with your actual organization name if needed.
    """
    # Construct the clone URL with PAT in it
    clone_url = f"https://{ADO_TOKEN}@dev.azure.com/yourorganization/{project}/_git/{repo_name}"
    clone_cmd = f"git clone {clone_url}"
    print(f"Cloning repository '{repo_name}' from project '{project}'...")
    result = subprocess.run(clone_cmd, shell=True)
    return result.returncode == 0

def run_cloc(repo_name):
    """
    Runs cloc.pl on the cloned repository directory and generates a CSV report.
    The report is saved as <repo_name>.csv in a folder structure: cloc_reports/<project>/.
    """
    output_file = f"{repo_name}.csv"
    cloc_cmd = f"perl cloc.pl {repo_name} --csv --out={output_file}"
    print(f"Running cloc.pl on '{repo_name}' (output: {output_file})...")
    result = subprocess.run(cloc_cmd, shell=True)
    return (result.returncode == 0, output_file)

def publish_artifact(report_path, project, repo_name):
    """
    Publishes the CSV report as a pipeline artifact using the Azure DevOps logging command.
    The logging command printed to STDOUT is detected by the build agent.
    """
    if os.path.exists(report_path):
        abs_path = os.path.abspath(report_path)
        # The artifact name is set as "<project>/<repo_name>_cloc"
        print(f"##vso[artifact.upload artifactname={project}/{repo_name}_cloc]{abs_path}")
        print(f"Published artifact for repository '{repo_name}' from project '{project}'.")
    else:
        print(f"Artifact file {report_path} not found for repository '{repo_name}'.")

def cleanup_repository(repo_name):
    """Deletes the cloned repository folder."""
    cleanup_cmd = f"rm -rf {repo_name}"
    print(f"Cleaning up repository folder '{repo_name}'...")
    subprocess.run(cleanup_cmd, shell=True)

def main():
    # Ensure cloc.pl exists in the repo
    if not os.path.exists("cloc.pl"):
        print("cloc.pl not found. Please ensure cloc.pl is available and executable in the repository.")
        return

    # Read project names from the file
    if not os.path.exists(PROJECTS_FILE):
        print(f"{PROJECTS_FILE} not found. Please create a file with one project name per line.")
        return

    with open(PROJECTS_FILE, "r") as f:
        projects = [line.strip() for line in f if line.strip()]

    if not projects:
        print("No projects found in the file.")
        return

    # Process each project
    for project in projects:
        print(f"\n=== Processing project: {project} ===")
        repos = list_repositories(project)
        if not repos:
            print(f"No repositories found for project '{project}'.")
            continue

        # Process each repository in the project
        for repo in repos:
            repo_name = repo.get("name")
            if not repo_name:
                continue

            print(f"\n--- Processing repository: {repo_name} ---")
            if clone_repository(project, repo_name):
                success, report_path = run_cloc(repo_name)
                if success:
                    publish_artifact(report_path, project, repo_name)
                else:
                    print(f"Failed to run cloc.pl for repository '{repo_name}'.")
                cleanup_repository(repo_name)
            else:
                print(f"Failed to clone repository '{repo_name}'.")

if __name__ == "__main__":
    main()