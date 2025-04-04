import csv
import os
import subprocess

# Set your Azure DevOps org URL and PAT token environment variable
AZURE_DEVOPS_ORG = "https://dev.azure.com/YOUR_ORG_NAME"
PAT = os.getenv("TOKEN")  # Make sure the TOKEN env var is set securely
FILE_TO_ECHO = "README.md"  # Replace with your desired file

def clone_repo(project, repo):
    clone_url = f"{AZURE_DEVOPS_ORG}/{project}/_git/{repo}"
    auth_url = clone_url.replace("https://", f"https://{PAT}@")
    repo_dir = f"{project}_{repo}"

    if not os.path.exists(repo_dir):
        try:
            subprocess.run(["git", "clone", auth_url, repo_dir], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to clone {repo} from {project}")
            return None
    return repo_dir

def echo_file(repo_dir, file_name):
    file_path = os.path.join(repo_dir, file_name)
    if os.path.exists(file_path):
        print(f"\n--- Content of {file_name} in {repo_dir} ---")
        with open(file_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(f"{file_name} not found in {repo_dir}")

def main():
    with open("repo.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            project = row["Project Name"].strip()
            repo = row["Repository Name"].strip()
            repo_dir = clone_repo(project, repo)
            if repo_dir:
                echo_file(repo_dir, FILE_TO_ECHO)

if __name__ == "__main__":
    main()