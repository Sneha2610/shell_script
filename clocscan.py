import os
import requests
import zipfile
import subprocess

# Hardcoded Azure DevOps configuration
ADO_ORG_URL = "https://dev.azure.com/yourorganization/"  # Replace with your actual organization URL
ADO_TOKEN = os.environ.get("TOKEN")  # Personal Access Token (set in the pipeline)
PROJECTS_FILE = "projects.txt"         # Contains one project name per line
AUTH = ('', ADO_TOKEN)

def download_repo_zip(project, repo_name):
    """
    Downloads a repository as a ZIP archive from Azure DevOps.
    This avoids performing a full git clone.
    """
    url = f"{ADO_ORG_URL}{project}/_apis/git/repositories/{repo_name}/items?scopePath=/&$format=zip&download=true&api-version=6.0"
    response = requests.get(url, auth=AUTH)
    if response.status_code == 200:
        zip_file = f"{repo_name}.zip"
        with open(zip_file, "wb") as f:
            f.write(response.content)
        return zip_file
    else:
        print(f"Failed to download {repo_name}: {response.status_code} - {response.text}")
        return None

def extract_zip(zip_file, extract_to):
    """Extracts the downloaded ZIP file."""
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def run_cloc(project, repo_dir, repo_name):
    """
    Runs cloc.pl on the extracted repository and saves output in CSV format.
    The CSV report will be stored in the folder structure:
      cloc_reports/<project>/<repo_name>_cloc.csv
    """
    report_folder = os.path.join("cloc_reports", project)
    os.makedirs(report_folder, exist_ok=True)
    report_path = os.path.join(report_folder, f"{repo_name}_cloc.csv")
    cloc_command = f"perl cloc.pl {repo_dir} --csv --out={report_path}"
    print(f"Executing: {cloc_command}")
    result = subprocess.run(cloc_command, shell=True)
    return result.returncode == 0, report_path

def publish_artifact(report_path, project, repo_name):
    """
    Publishes the CSV report as an artifact using the Azure DevOps logging command.
    The logging command printed to STDOUT is picked up by the build agent.
    """
    if os.path.exists(report_path):
        abs_path = os.path.abspath(report_path)
        # The artifact name here is formed as "<project>/<repo_name>_cloc"
        print(f"##vso[artifact.upload artifactname={project}/{repo_name}_cloc]{abs_path}")
        print(f"Published artifact for repository: {repo_name}")
    else:
        print(f"Artifact file {report_path} not found.")

def main():
    # Ensure cloc.pl exists in the repository (it should be committed to your repo)
    if not os.path.exists("cloc.pl"):
        print("cloc.pl not found in the repository. Please ensure it is available and executable.")
        return

    # Read project names from file (each line should contain one project name)
    if not os.path.exists(PROJECTS_FILE):
        print("Projects file not found.")
        return

    with open(PROJECTS_FILE, "r") as file:
        projects = [line.strip() for line in file if line.strip()]

    # Process each project in the file
    for project in projects:
        print(f"Processing project: {project}")
        url = f"{ADO_ORG_URL}{project}/_apis/git/repositories?api-version=6.0"
        response = requests.get(url, auth=AUTH)

        if response.status_code != 200:
            print(f"Failed to fetch repositories for {project}. Error: {response.status_code} - {response.text}")
            continue

        repos = response.json().get("value", [])

        for repo in repos:
            repo_name = repo["name"]
            print(f"Downloading repository: {repo_name}")
            zip_file = download_repo_zip(project, repo_name)
            if zip_file:
                extract_folder = f"./{repo_name}"
                extract_zip(zip_file, extract_folder)

                print(f"Running CLOC on {repo_name}")
                success, report_path = run_cloc(project, extract_folder, repo_name)
                if success:
                    print(f"Publishing artifact for {repo_name}")
                    publish_artifact(report_path, project, repo_name)
                else:
                    print(f"Failed to run CLOC for {repo_name}")

                # Cleanup: Remove the ZIP file and extracted folder
                os.remove(zip_file)
                subprocess.run(f"rm -rf {extract_folder}", shell=True)

if __name__ == "__main__":
    main()