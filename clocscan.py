import os
import subprocess
import csv
import sys

# Azure DevOps configuration
ADO_ORG_URL = "https://dev.azure.com/yourorganization/"  # Replace with your actual organization URL
ADO_TOKEN = os.environ.get("TOKEN")  # Personal Access Token from pipeline
CSV_FILE = "projectandrepos.csv"  # CSV containing Project Name and Repository Name columns
REPORTS_DIR = "Reports"  # Base directory for reports

def validate_cloc_path(cloc_path):
    """Validates if the given cloc.pl path exists."""
    if not os.path.isfile(cloc_path):
        print(f"cloc.pl not found at {cloc_path}. Please provide a valid path.")
        sys.exit(1)

def clone_repository(project, repo_name):
    """Clones the specified repository."""
    clone_url = f"https://{ADO_TOKEN}@dev.azure.com/yourorganization/{project}/_git/{repo_name}"
    clone_cmd = f"git clone {clone_url}"
    print(f"Cloning repository '{repo_name}' from project '{project}'...")
    result = subprocess.run(clone_cmd, shell=True)
    return result.returncode == 0

def run_cloc(cloc_path, project, repo_name):
    """Runs cloc.pl on the cloned repository and generates a CSV report in the Reports/{project}/{repo}.csv path."""
    # Create project-specific directory
    project_report_dir = os.path.join(REPORTS_DIR, project)
    os.makedirs(project_report_dir, exist_ok=True)

    output_file = os.path.join(project_report_dir, f"{repo_name}.csv")
    cloc_cmd = f"perl {cloc_path} {repo_name} --csv --out={output_file}"
    print(f"Running cloc.pl on '{repo_name}' (output: {output_file})...")
    result = subprocess.run(cloc_cmd, shell=True)
    return (result.returncode == 0, output_file)

def publish_artifact(report_path, project, repo_name):
    """Publishes the CSV report as a pipeline artifact using Azure DevOps logging command."""
    if os.path.exists(report_path):
        abs_path = os.path.abspath(report_path)
        print(f"##vso[artifact.upload artifactname={project}/{repo_name}_cloc]{abs_path}")
        print(f"Published artifact for repository '{repo_name}' from project '{project}'.")
    else:
        print(f"Artifact file {report_path} not found for repository '{repo_name}'.")

def cleanup_repository(repo_name):
    """Deletes the cloned repository folder."""
    cleanup_cmd = f"rm -rf {repo_name}"
    print(f"Cleaning up repository folder '{repo_name}'...")
    subprocess.run(cleanup_cmd, shell=True)

def main(cloc_path):
    # Validate cloc.pl path
    validate_cloc_path(cloc_path)

    # Read project and repository list from CSV
    if not os.path.exists(CSV_FILE):
        print(f"{CSV_FILE} not found. Please ensure the CSV exists.")
        return

    with open(CSV_FILE, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            project = row.get("Project Name")
            repo_name = row.get("Repository Name")

            if not project or not repo_name:
                print("Missing project or repository name in CSV. Skipping...")
                continue

            print(f"\n--- Processing repository '{repo_name}' from project '{project}' ---")
            if clone_repository(project, repo_name):
                success, report_path = run_cloc(cloc_path, project, repo_name)
                if success:
                    publish_artifact(report_path, project, repo_name)
                else:
                    print(f"Failed to run cloc.pl for repository '{repo_name}'.")
                cleanup_repository(repo_name)
            else:
                print(f"Failed to clone repository '{repo_name}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_cloc.pl>")
        sys.exit(1)

    cloc_script_path = sys.argv[1]
    main(cloc_script_path)