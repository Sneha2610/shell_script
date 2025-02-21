import os
import requests
import zipfile
import subprocess

# Hardcoded Azure DevOps configuration
ADO_ORG_URL = "https://dev.azure.com/yourorganization/"  # Replace with your actual organization URL
ADO_TOKEN = os.environ.get("TOKEN")  # Personal Access Token (set in pipeline)
PROJECTS_FILE = "projects.txt"
AUTH = ('', ADO_TOKEN)

def download_repo_zip(project, repo_name):
    """Downloads a repository as a zip archive from Azure DevOps."""
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
    """Extracts the downloaded zip file."""
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def run_cloc(project, repo_dir, repo_name):
    """Runs cloc.pl on the extracted repository and saves output in CSV format."""
    report_folder = os.path.join("cloc_reports", project)
    os.makedirs(report_folder, exist_ok=True)
    report_path = os.path.join(report_folder, f"{repo_name}_cloc.csv")
    cloc_command = f"perl cloc.pl {repo_dir} --csv --out={report_path}"
    result = subprocess.run(cloc_command, shell=True)
    return result.returncode == 0, report_path

def publish_artifact(report_path, project, repo_name):
    """Moves the artifact to a staging directory for Azure DevOps to publish."""
    artifact_staging_dir = os.environ.get("BUILD_ARTIFACTSTAGINGDIRECTORY", "artifact_staging")
    destination_folder = os.path.join(artifact_staging_dir, project)
    os.makedirs(destination_folder, exist_ok=True)
    destination_path = os.path.join(destination_folder, f"{repo_name}_cloc.csv")

    try:
        os.rename(report_path, destination_path)
        print(f"Artifact moved to: {destination_path}")
    except Exception as e:
        print(f"Failed to move artifact for {repo_name}: {e}")

def main():
    # Assuming cloc.pl is available in the repo
    if not os.path.exists("cloc.pl"):
        print("cloc.pl not found in the repository.")
        return

    # Read projects from file
    if not os.path.exists(PROJECTS_FILE):
        print("Projects file not found.")
        return

    with open(PROJECTS_FILE, "r") as file:
        projects = [line.strip() for line in file if line.strip()]

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

                # Cleanup extracted files and zip
                os.remove(zip_file)
                subprocess.run(f"rm -rf {extract_folder}", shell=True)

if __name__ == "__main__":
    main()