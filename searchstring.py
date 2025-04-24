import requests
import csv
import os
import sys

# --- CONFIGURATION ---
ADO_ORG_URL = "https://dev.azure.com/YOUR_ORG"  # Replace with your org
SEARCH_STRING = "your_search_string"  # Replace with the string you're looking for
CSV_OUTPUT = "search_results.csv"
PAT = os.environ.get("ADO_PAT")  # PAT should be passed securely

if not PAT:
    sys.exit("Environment variable ADO_PAT not set")

auth = requests.auth.HTTPBasicAuth("", PAT)
headers = {"Content-Type": "application/json"}
proxies = {"http": None, "https": None}  # Disable proxy for some networks


def get_projects():
    url = f"{ADO_ORG_URL}/_apis/projects?api-version=7.0"
    resp = requests.get(url, auth=auth, proxies=proxies)
    resp.raise_for_status()
    return [proj["name"] for proj in resp.json()["value"]]


def get_repos(project):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories?api-version=7.0"
    resp = requests.get(url, auth=auth, proxies=proxies)
    resp.raise_for_status()
    return resp.json()["value"]


def get_release_branches(project, repo_id):
    url = f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/refs?filter=refs/heads/release/&api-version=7.0"
    resp = requests.get(url, auth=auth, proxies=proxies)
    resp.raise_for_status()
    return [ref["name"].split("refs/heads/")[1] for ref in resp.json()["value"]]


def get_file_content(project, repo_id, branch_name, path):
    url = (
        f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items"
        f"?path={path}&versionDescriptor.version={branch_name}"
        f"&versionDescriptor.versionType=branch&includeContent=true&api-version=7.0"
    )
    resp = requests.get(url, auth=auth, proxies=proxies)
    if resp.status_code == 200:
        return resp.text
    return None


def search_branch_files(project, repo_name, repo_id, branch_name, writer, csvfile):
    url = (
        f"{ADO_ORG_URL}/{project}/_apis/git/repositories/{repo_id}/items"
        f"?recursionLevel=Full&versionDescriptor.version={branch_name}"
        f"&versionDescriptor.versionType=branch&includeContentMetadata=true"
        f"&api-version=7.0"
    )
    resp = requests.get(url, auth=auth, proxies=proxies)
    resp.raise_for_status()
    for item in resp.json().get("value", []):
        path = item.get("path")
        is_folder = item.get("isFolder", False)

        if not is_folder and path.endswith(('.py', '.yml', '.yaml', '.txt', '.json', '.md', '.sh', '.cs', '.java', '.js')):
            content = get_file_content(project, repo_id, branch_name, path)
            if content and SEARCH_STRING in content:
                for i, line in enumerate(content.splitlines(), 1):
                    if SEARCH_STRING in line:
                        log_msg = f"[FOUND] {SEARCH_STRING} in {project}/{repo_name}{path} at line {i}"
                        print(log_msg)
                        writer.writerow({
                            "search_string": SEARCH_STRING,
                            "project": project,
                            "repository": repo_name,
                            "file_path": path,
                            "line_number": i
                        })
                        csvfile.flush()


def main():
    with open(CSV_OUTPUT, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["search_string", "project", "repository", "file_path", "line_number"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        try:
            projects = get_projects()
        except Exception as e:
            sys.exit(f"Failed to get projects: {e}")

        for project in projects:
            print(f"\n[INFO] Scanning project: {project}")
            try:
                repos = get_repos(project)
            except Exception as e:
                print(f"[ERROR] Failed to get repos for project {project}: {e}")
                continue

            for repo in repos:
                repo_id = repo["id"]
                repo_name = repo["name"]
                print(f"[INFO]  Scanning repo: {repo_name}")
                try:
                    release_branches = get_release_branches(project, repo_id)
                except Exception as e:
                    print(f"[ERROR] Failed to get release branches for {repo_name}: {e}")
                    continue

                for branch in release_branches:
                    print(f"[INFO]   Scanning branch: {branch}")
                    try:
                        search_branch_files(project, repo_name, repo_id, branch, writer, csvfile)
                    except Exception as e:
                        print(f"[ERROR] Failed to scan branch {branch} in {repo_name}: {e}")


if __name__ == "__main__":
    main()