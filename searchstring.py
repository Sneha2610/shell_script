import os
import csv
import requests
import concurrent.futures

# === CONFIG ===
ADO_ORG_URL = "https://dev.azure.com/<your_org>"  # CHANGE this
SEARCH_STRING = "your_search_string"              # CHANGE this
OUTPUT_FILE = "ado_search_results.csv"

# === Setup ===
PAT = os.environ.get("ADO_PAT")
if not PAT:
    raise EnvironmentError("Environment variable ADO_PAT is not set.")
auth = ("", PAT)
HEADERS = {"Content-Type": "application/json"}

# Write CSV header once
with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Search String", "Project", "Repo", "File Path", "Line Number"])

def log_and_write(row):
    print("MATCH FOUND:", row)
    with open(OUTPUT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def get_projects():
    url = f"{ADO_ORG_URL}/_apis/projects?api-version=7.0"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return [p["name"] for p in r.json()["value"]]

def get_repos(project):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories?api-version=7.0"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return r.json()["value"]

def get_release_branches(project, repo_id):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/refs?filter=heads/release/&api-version=7.0"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return [b["name"].replace("refs/heads/", "") for b in r.json()["value"]]

def get_files(project, repo_id, branch):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items?recursionLevel=Full&versionDescriptor.version={branch}&api-version=7.0"
    r = requests.get(url, auth=auth)
    r.raise_for_status()
    return [item["path"] for item in r.json()["value"] if item["gitObjectType"] == "blob"]

def get_file_content(project, repo_id, path, branch):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items?path={path}&versionDescriptor.version={branch}&includeContent=true&api-version=7.0"
    r = requests.get(url, auth=auth)
    if r.status_code == 200:
        return r.text
    return ""

def search_file(project, repo_name, repo_id, branch, path):
    try:
        content = get_file_content(project, repo_id, path, branch)
        for i, line in enumerate(content.splitlines(), 1):
            if SEARCH_STRING in line:
                log_and_write([SEARCH_STRING, project, repo_name, path, i])
    except Exception as e:
        print(f"[ERROR] File read failed: {path} in {repo_name}: {e}")

def process_repo(project, repo):
    repo_id = repo["id"]
    repo_name = repo["name"]
    try:
        branches = get_release_branches(project, repo_id)
        for branch in branches:
            files = get_files(project, repo_id, branch)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for path in files:
                    executor.submit(search_file, project, repo_name, repo_id, branch, path)
    except Exception as e:
        print(f"[ERROR] Repo: {repo_name} in {project} — {e}")

def main():
    try:
        projects = get_projects()
        for project in projects:
            repos = get_repos(project)
            for repo in repos:
                process_repo(project, repo)
    except Exception as e:
        print(f"[ERROR] Failed to scan: {e}")

if __name__ == "__main__":
    main()