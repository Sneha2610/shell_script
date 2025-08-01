import os
import csv
import base64
import requests
from git import Repo
from tempfile import mkdtemp
import shutil

CSV_INPUT = "data/projectandrepo1.csv"
CSV_OUTPUT = "nosonar_report.csv"
ADO_PAT = os.getenv("TOKEN")  # Retrieved from pipeline environment variable
ADO_ORG_URL = "https://dev.azure.com/YOUR_ORG"  # Replace with your actual org URL

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f':{ADO_PAT}'.encode()).decode()
}

def get_repo_url(project, repo_name):
    """Fetch remote URL for given project and repo."""
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_name}?api-version=6.0"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        raise Exception(f"Failed to get repo URL for {project}/{repo_name}: {resp.text}")
    return resp.json()["remoteUrl"]

def scan_repo(project, repo_name, repo_url, writer):
    temp_dir = mkdtemp()
    try:
        print(f"Cloning {project}/{repo_name}")
        secure_url = repo_url.replace("https://", f"https://{ADO_PAT}@")
        Repo.clone_from(secure_url, temp_dir, depth=1)

        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, start=1):
                            if "NOSONAR" in line:
                                rel_path = os.path.relpath(file_path, temp_dir)
                                writer.writerow([project, repo_name, rel_path, i, line.strip()])
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
    finally:
        shutil.rmtree(temp_dir)

def main():
    if not os.path.exists(CSV_INPUT):
        print(f"Input CSV not found at {CSV_INPUT}")
        return

    with open(CSV_INPUT, newline='', encoding='utf-8') as infile, \
         open(CSV_OUTPUT, "w", newline='', encoding="utf-8") as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile)
        writer.writerow(["Project", "Repository", "File", "Line Number", "Line"])

        for row in reader:
            project = row.get("Project")
            repo = row.get("Repo Name")

            if not project or not repo:
                print("Missing project or repo in row, skipping...")
                continue

            try:
                repo_url = get_repo_url(project, repo)
                scan_repo(project, repo, repo_url, writer)
            except Exception as e:
                print(f"Failed processing {project}/{repo}: {e}")

    print(f"\n✅ NOSONAR scan completed. Results saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    main()