import os
import csv
import tempfile
import shutil
import fnmatch
import subprocess
from concurrent.futures import ThreadPoolExecutor
from git import Repo
import requests
import base64

# === CONFIG ===
ADO_ORG = "your-org"  # <-- Replace with your ADO org name
ADO_URL = f"https://dev.azure.com/{ADO_ORG}"
SEARCH_STRING = "your_search_string"  # <-- Replace with your target string
CSV_FILE = "release_search_results.csv"
THREADS = 5

# === AUTH ===
PAT = os.getenv("ADO_PAT")
if not PAT:
    raise Exception("ADO_PAT environment variable not set")

AUTH_HEADER = {
    "Authorization": f"Basic {base64.b64encode(f':{PAT}'.encode()).decode()}"
}


def get_projects():
    url = f"{ADO_URL}/_apis/projects?api-version=7.0"
    resp = requests.get(url, headers=AUTH_HEADER)
    resp.raise_for_status()
    return [p["name"] for p in resp.json()["value"]]


def get_repos(project):
    url = f"{ADO_URL}/{project}/_apis/git/repositories?api-version=7.0"
    resp = requests.get(url, headers=AUTH_HEADER)
    resp.raise_for_status()
    return [(r["name"], r["remoteUrl"]) for r in resp.json()["value"]]


def clone_and_search(project, repo_name, remote_url):
    print(f"[CLONE] {project}/{repo_name}")
    workdir = tempfile.mkdtemp()
    try:
        repo_path = os.path.join(workdir, repo_name)
        # Clone as mirror to quickly fetch all refs
        repo = Repo.clone_from(remote_url, repo_path, multi_options=['--mirror'])

        # Get all branches matching release/*
        refs = subprocess.check_output(
            ["git", "--git-dir", repo_path, "for-each-ref", "--format=%(refname:short)"],
            text=True
        )
        branches = [ref for ref in refs.splitlines() if fnmatch.fnmatch(ref, "release/*")]

        for branch in branches:
            print(f"[BRANCH] {repo_name}: {branch}")
            branch_dir = os.path.join(workdir, f"{repo_name}_{branch.replace('/', '_')}")
            full_clone = Repo.clone_from(remote_url, branch_dir, branch=branch, depth=1)
            repo_dir = full_clone.working_tree_dir

            for root, _, files in os.walk(repo_dir):
                for file in files:
                    try:
                        path = os.path.join(root, file)
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if SEARCH_STRING in line:
                                    relative = os.path.relpath(path, repo_dir)
                                    row = [SEARCH_STRING, project, repo_name, branch, relative, i]
                                    print("FOUND:", row)
                                    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as fcsv:
                                        csv.writer(fcsv).writerow(row)
                    except Exception as e:
                        print(f"[ERROR] Reading file {file} in {repo_name}: {e}")
    except Exception as e:
        print(f"[ERROR] Failed {project}/{repo_name}: {e}")
    finally:
        shutil.rmtree(workdir)


def main():
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["Search String", "Project", "Repo", "Branch", "File Path", "Line Number"])

    try:
        projects = get_projects()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch projects: {e}")
        return

    jobs = []
    for project in projects:
        try:
            repos = get_repos(project)
            for repo_name, remote_url in repos:
                # Add PAT to remote URL
                if "@dev.azure.com" in remote_url:
                    remote_url = remote_url.replace("https://", f"https://{PAT}@")
                jobs.append((project, repo_name, remote_url))
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch repos for project {project}: {e}")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        for job in jobs:
            executor.submit(clone_and_search, *job)


if __name__ == "__main__":
    main()